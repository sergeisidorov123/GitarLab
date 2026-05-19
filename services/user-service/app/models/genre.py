from sqlalchemy import Column, String, Integer
from app.core.database import Base


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
