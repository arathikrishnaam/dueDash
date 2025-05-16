# init_db.py
from sqlmodel import SQLModel
from app.db.database import engine
from app.models import User, Todo  

SQLModel.metadata.create_all(engine)
