from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.database import get_session
from app.models import User, UserCreate, Todo, TodoCreate, TodoUpdate
from app.auth import get_password_hash, create_access_token, get_user, get_current_user, verify_password
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

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