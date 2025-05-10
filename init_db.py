# init_db.py
from sqlmodel import SQLModel
from database import engine
from models import User, Todo  

SQLModel.metadata.create_all(engine)
