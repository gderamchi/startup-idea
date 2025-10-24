"""
Action Item Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ActionItemBase(BaseModel):
    description: str = Field(..., min_length=1)
    priority: int = Field(default=0, ge=0, le=3)

class ActionItemCreate(ActionItemBase):
    feedback_id: UUID

class ActionItemUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    is_completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=3)

class ActionItemResponse(ActionItemBase):
    id: UUID
    feedback_id: UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
