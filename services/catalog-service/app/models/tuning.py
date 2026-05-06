from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Tuning(Base):
    __tablename__ = "tunings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)   
    string_names = Column(JSON, nullable=False)               
    frequencies = Column(JSON, nullable=False)                
    
    songs = relationship("Song", back_populates="tuning")