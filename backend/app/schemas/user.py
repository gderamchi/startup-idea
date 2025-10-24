"""
User Schemas
Pydantic models for user-related requests and responses
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """Schema for user response (public data)"""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)"""
    hashed_password: str
    is_superuser: bool = False
    
    model_config = {"from_attributes": True}


class UserProfile(UserResponse):
    """Extended user profile with statistics"""
    total_projects: int = 0
    total_feedbacks: int = 0
    total_revisions: int = 0
    
    model_config = {"from_attributes": True}
