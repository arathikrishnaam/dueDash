from sqlmodel import create_engine, Session
from contextlib import contextmanager

DATABASE_URL = "postgresql://postgres:813883@localhost/todoapp"
engine = create_engine(DATABASE_URL)

@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()