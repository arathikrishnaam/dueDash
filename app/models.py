from sqlmodel import Field, SQLModel
from datetime import datetime
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password: str

class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    due_time: datetime
    completed: bool = False
    user_id: int = Field(foreign_key="user.id")

class UserCreate(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    due_time: datetime

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_time: datetime | None = None
    completed: bool | None = None