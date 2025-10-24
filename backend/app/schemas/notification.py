"""
Notification Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: Optional[str] = None
    is_read: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class NotificationUpdate(BaseModel):
    is_read: bool = True
