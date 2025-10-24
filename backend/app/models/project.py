"""
Project Model
Represents projects that contain feedback and revisions
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.types import UUID


class Project(Base):
    """
    Project model for organizing feedback and revisions
    """
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Project details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)  # active, archived, completed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    feedbacks = relationship("Feedback", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
