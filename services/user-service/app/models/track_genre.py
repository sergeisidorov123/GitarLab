from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class TrackGenre(Base):
    __tablename__ = "track_genres"

    track_id = Column(String(50), ForeignKey("tracks.id"), primary_key=True, nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    track = relationship("Track", back_populates="genres")
    genre = relationship("Genre")
