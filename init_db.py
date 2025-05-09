from sqlmodel import SQLModel
from database import engine

SQLModel.metadata.create_all(engine)