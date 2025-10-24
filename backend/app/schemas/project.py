"""
Project Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
