"""
Notification Management Endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationUpdate

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def list_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List user notifications"""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return notifications

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mark notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    if not notification.is_read:
        from datetime import datetime
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)
    
    return notification

@router.put("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Mark all notifications as read"""
    from datetime import datetime
    
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    
    db.commit()
    return {"message": "All notifications marked as read"}

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}
