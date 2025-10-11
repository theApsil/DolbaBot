from sqlalchemy import (
    Column, Integer, DateTime, Float
)
from sqlalchemy.orm import (
    declarative_base
)

Base = declarative_base()

class Course(Base):
    __tablename__ = "course"
    __table_args__ = {'schema': None}

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    course = Column(Float, nullable=False)
