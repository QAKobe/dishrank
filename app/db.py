# app/db.py
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

engine = create_engine("sqlite:///./dishrank.db", connect_args={"check_same_thread": False})

class Dish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    place: str
    name: str
    category: str
    rating: float
    nickname: str | None = None          # 👈 who submitted
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
