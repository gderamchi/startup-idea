"""
User Management Endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update current user profile"""
    if user_update.email:
        current_user.email = user_update.email
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.password:
        from app.core.security import get_password_hash
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete current user account"""
    db.delete(current_user)
    db.commit()
