"""
Notification Model
Represents user notifications for feedback and approvals
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.types import UUID


class Notification(Base):
    """
    Notification model for user alerts and updates
    """
    
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification details
    type = Column(String(50), nullable=False)  # feedback_received, revision_uploaded, approval_requested, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Additional data (JSON)
    meta_data = Column(JSON, nullable=True)  # Store related IDs, links, etc. (using JSON instead of JSONB for SQLite compatibility)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, is_read={self.is_read})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "metadata": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }
