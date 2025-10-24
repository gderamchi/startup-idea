"""
Revision Management Endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.revision import Revision
from app.models.feedback import Feedback
from app.schemas.revision import RevisionCreate, RevisionUpdate, RevisionResponse

router = APIRouter()

@router.post("/", response_model=RevisionResponse, status_code=status.HTTP_201_CREATED)
async def create_revision(
    feedback_id: UUID,
    notes: str = None,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Upload a new revision"""
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
    
    # Get next version number
    last_revision = db.query(Revision).filter(
        Revision.feedback_id == feedback_id
    ).order_by(Revision.version.desc()).first()
    
    next_version = (last_revision.version + 1) if last_revision else 1
    
    # Create revision
    revision = Revision(
        feedback_id=feedback_id,
        version=next_version,
        notes=notes,
        status="pending"
    )
    
    # Handle file upload if provided
    if file:
        # TODO: Implement file storage
        revision.file_name = file.filename
        revision.file_type = file.content_type
    
    db.add(revision)
    db.commit()
    db.refresh(revision)
    
    return revision

@router.get("/{revision_id}", response_model=RevisionResponse)
def get_revision(
    revision_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get revision by ID"""
    revision = db.query(Revision).join(Feedback).filter(
        Revision.id == revision_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    return revision

@router.get("/feedback/{feedback_id}/revisions", response_model=List[RevisionResponse])
def list_feedback_revisions(
    feedback_id: UUID,
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
    ).order_by(Revision.version.desc()).all()
    return revisions

@router.put("/{revision_id}", response_model=RevisionResponse)
def update_revision(
    revision_id: UUID,
    revision_update: RevisionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update revision status or notes"""
    revision = db.query(Revision).join(Feedback).filter(
        Revision.id == revision_id,
        Feedback.user_id == current_user.id
    ).first()
    
    if not revision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Revision not found"
        )
    
    update_data = revision_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(revision, field, value)
    
    if revision_update.status == "approved":
        from datetime import datetime
        revision.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(revision)
    return revision
