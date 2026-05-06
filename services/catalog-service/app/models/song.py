from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Song(Base):
    __tablename__ = "songs"
    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=False)
    tuning_id = Column(Integer, ForeignKey("tunings.id"), nullable=False)
    
    tuning = relationship("Tuning", back_populates="songs")