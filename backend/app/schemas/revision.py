"""
Revision Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class RevisionBase(BaseModel):
    feedback_id: UUID
    notes: Optional[str] = None

class RevisionCreate(RevisionBase):
    pass

class RevisionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class RevisionResponse(RevisionBase):
    id: UUID
    version: int
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
