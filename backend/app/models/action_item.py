"""
Action Item Model
Represents actionable tasks extracted from feedback
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text

from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.types import UUID


class ActionItem(Base):
    """
    Action Item model for tracking tasks extracted from feedback
    """
    
    __tablename__ = "action_items"
    
    # Primary key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    feedback_id = Column(UUID(), ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Action details
    description = Column(Text, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # 0=low, 1=medium, 2=high, 3=urgent
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="action_items")
    
    def __repr__(self) -> str:
        return f"<ActionItem(id={self.id}, completed={self.is_completed})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "feedback_id": str(self.feedback_id),
            "description": self.description,
            "is_completed": self.is_completed,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
