from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False, index=True)
    author_username = Column(String, nullable=False)
    track_id = Column(String, nullable=False, index=True)  # Reference to track from user-service
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # For nested replies
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    replies = relationship("Comment", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Comment(id={self.id}, author={self.author_username}, track={self.track_id})>"