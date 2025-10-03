from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from db.models import Base
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

SessionLocal = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
