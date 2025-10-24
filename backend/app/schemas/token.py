"""
Token Schemas
Authentication token models
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: UUID  # User ID
    email: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    type: str = "access"  # access or refresh


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str
