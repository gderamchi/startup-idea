"""
Feedback Model
Represents client feedback with AI-parsed summaries
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.types import UUID


class Feedback(Base):
    """
    Feedback model for storing and parsing client feedback
    """
    
    __tablename__ = "feedbacks"
    
    # Primary key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(UUID(), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Feedback content
    raw_text = Column(Text, nullable=False)
    summary = Column(JSON, nullable=True)  # AI-generated summary as JSON (using JSON instead of JSONB for SQLite compatibility)
    
    # AI analysis
    sentiment = Column(String(50), nullable=True)  # positive, neutral, negative
    priority = Column(String(50), nullable=True)  # low, medium, high, urgent
    
    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, in_progress, completed, archived
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")
    project = relationship("Project", back_populates="feedbacks")
    revisions = relationship("Revision", back_populates="feedback", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="feedback", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, project_id={self.project_id}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "project_id": str(self.project_id),
            "raw_text": self.raw_text,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
