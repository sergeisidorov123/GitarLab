import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=False)
    tuning_name = Column(String(150), nullable=False)
    string_names = Column(JSON, nullable=False)
    frequencies = Column(JSON, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="tracks")
    favorites = relationship("Favorite", back_populates="track")
    genres = relationship("TrackGenre", back_populates="track", cascade="all, delete-orphan")
