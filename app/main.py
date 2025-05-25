from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.database import get_session
from app.models import User, UserCreate, Todo, TodoCreate, TodoUpdate
from app.auth import get_password_hash, create_access_token, get_user, get_current_user, verify_password
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
import os

app = FastAPI(title="dueDash API", description="A simple todo application API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health", tags=["Health"])
def health_check():
    """Check if the API is running"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/health/db", tags=["Health"])
def db_health_check(db: Session = Depends(get_session)):
    """Check if the database connection is working"""
    try:
        # Simple query to check DB connectivity
        db.exec(select(1)).first()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}

# Root Endpoint
@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint for the API"""
    return {"message": "Welcome to dueDash", "docs_url": "/docs"}

# Authentication Endpoints
@app.post("/signup", tags=["Authentication"])
def signup(user: UserCreate, db: Session = Depends(get_session)):
    """Register a new user"""
    existing_user = get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "username": new_user.username}

@app.post("/login", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    """Login to get access token"""
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Todo Endpoints
@app.post("/todos", tags=["Todos"])
def create_todo(todo: TodoCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Create a new todo item"""
    new_todo = Todo(**todo.dict(), user_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos", tags=["Todos"])
def read_todos(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get all todos for the current user, grouped by status"""
    todos = db.exec(select(Todo).where(Todo.user_id == current_user.id)).all()
    now = datetime.utcnow()
    completed = [todo for todo in todos if todo.completed]
    to_be_done = [todo for todo in todos if not todo.completed and todo.due_time >= now]
    overdue = [todo for todo in todos if not todo.completed and todo.due_time < now]
    return {"completed": completed, "to_be_done": to_be_done, "overdue": overdue}

@app.get("/todos/{todo_id}", tags=["Todos"])
def read_todo(todo_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a specific todo by ID"""
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@app.patch("/todos/{todo_id}", tags=["Todos"])
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Update a todo item"""
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    update_data = todo_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(todo, key, value)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.patch("/todos/{todo_id}/complete", tags=["Todos"])
def complete_todo(todo_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Mark a todo as completed"""
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    todo.completed = True
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}", tags=["Todos"])
def delete_todo(todo_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Delete a todo item"""
    todo = db.exec(select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted"}

# WebSocket Implementation
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}  # websocket -> username

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[websocket] = username
        await self.broadcast_system(f"{username} joined the chat")

    def disconnect(self, websocket: WebSocket) -> str:
        return self.active_connections.pop(websocket, None)

    async def broadcast_system(self, message: str):
        if not self.active_connections:
            return
        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(f"System: {message}")
            except:
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.active_connections.pop(ws, None)

    async def broadcast(self, message: str, sender_websocket: WebSocket = None):
        if not self.active_connections:
            return
        disconnected = []
        for websocket, username in self.active_connections.items():
            if websocket != sender_websocket:
                try:
                    await websocket.send_text(message)
                except:
                    disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.active_connections.pop(ws, None)

manager = ConnectionManager()


def verify_token_and_get_user(token: str, db: Session) -> User:
    """Verify JWT token and return user using existing auth system"""
    try:
        from jose import jwt, JWTError
        import os
        
        SECRET_KEY = os.environ.get("SECRET_KEY")
        ALGORITHM = os.environ.get("ALGORITHM", "HS256")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = get_user(db, username)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@app.websocket("/ws/todos")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_session)
):
    try:
        # Verify token and get user
        user = verify_token_and_get_user(token, db)
        
        # Connect with username
        await manager.connect(websocket, user.username)
        
        while True:
            data = await websocket.receive_text()
            # Broadcast with username
            await manager.broadcast(
                message=f"{user.username}: {data}",
                sender_websocket=websocket
            )
            
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        username = manager.disconnect(websocket)
        if username:
            await manager.broadcast_system(f"{username} left the chat")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

# Simple WebSocket without authentication (for testing)
@app.websocket("/ws/test")
async def websocket_test_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)