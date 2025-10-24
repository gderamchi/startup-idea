"""
Feedback Management Endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.feedback import Feedback
from app.models.project import Project
from app.models.action_item import ActionItem
from app.models.revision import Revision
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse
from app.schemas.action_item import ActionItemResponse
from app.schemas.revision import RevisionResponse

router = APIRouter()

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Submit new feedback for AI parsing"""
    # Verify project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == feedback_in.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Create feedback
    feedback = Feedback(
        **feedback_in.model_dump(),
        user_id=current_user.id,
        status="pending"
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    # Queue AI parsing task
    # background_tasks.add_task(parse_feedback_task, feedback.id)
    
    return feedback

@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get feedback by ID"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback

@router.get("/project/{project_id}", response_model=List[FeedbackResponse])
def list_project_feedback(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List all feedback for a project"""
    feedbacks = db.query(Feedback).filter(
        Feedback.project_id == project_id,
        Feedback.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return feedbacks

@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(
    feedback_id: UUID,
    feedback_update: FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update feedback"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    update_data = feedback_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    db.commit()
    db.refresh(feedback)
    return feedback

@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete feedback"""
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    db.delete(feedback)
    db.commit()

@router.get("/{feedback_id}/actions", response_model=List[ActionItemResponse])
def list_action_items(
    feedback_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List all action items for a feedback"""
    # Verify feedback exists and belongs to user
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    action_items = db.query(ActionItem).filter(
        ActionItem.feedback_id == feedback_id
    ).offset(skip).limit(limit).all()
    return action_items

@router.get("/{feedback_id}/revisions", response_model=List[RevisionResponse])
def list_feedback_revisions(
    feedback_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List all revisions for a feedback"""
    # Verify feedback exists and belongs to user
    feedback = db.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    revisions = db.query(Revision).filter(
        Revision.feedback_id == feedback_id
    ).order_by(Revision.version.desc()).offset(skip).limit(limit).all()
    return revisions
