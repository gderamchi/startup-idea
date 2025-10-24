"""
Feedback Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class FeedbackBase(BaseModel):
    raw_text: str = Field(..., min_length=1, max_length=5000)
    project_id: UUID

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    raw_text: Optional[str] = Field(None, min_length=1, max_length=5000)
    status: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    id: UUID
    user_id: UUID
    summary: Optional[Dict[str, Any]] = None
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class FeedbackWithActions(FeedbackResponse):
    action_items: List[Dict[str, Any]] = []
