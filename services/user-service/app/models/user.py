from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    tracks = relationship("Track", back_populates="owner")
    favorites = relationship("Favorite", back_populates="user")
    tokens = relationship("Token", back_populates="user")

    @property
    def role_name(self):
        return self.role.name if self.role else "user"

    @property
    def is_admin(self):
        return self.role_name == "admin"

