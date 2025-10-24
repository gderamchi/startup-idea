"""
Revision Model
Represents file revisions and version tracking
"""

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text

from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.types import UUID


class Revision(Base):
    """
    Revision model for tracking file versions and approvals
    """
    
    __tablename__ = "revisions"
    
    # Primary key
    id = Column(UUID(), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign keys
    feedback_id = Column(UUID(), ForeignKey("feedbacks.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Version tracking
    version = Column(Integer, nullable=False)
    
    # File information
    file_url = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(BigInteger, nullable=True)  # Size in bytes
    file_type = Column(String(100), nullable=True)  # MIME type
    
    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected, in_review
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="revisions")
    
    def __repr__(self) -> str:
        return f"<Revision(id={self.id}, version={self.version}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "feedback_id": str(self.feedback_id),
            "version": self.version,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }
