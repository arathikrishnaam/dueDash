from sqlmodel import select, Session
from app.models import Todo

def get_todo(db: Session, todo_id: int, user_id: int):
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    return db.exec(statement).first()

def get_todos(db: Session, user_id: int):
    statement = select(Todo).where(Todo.user_id == user_id)
    return db.exec(statement).all()