#!/usr/bin/env python3
"""
Generate all API endpoint files
"""

import os
from pathlib import Path

ENDPOINTS = {
    "backend/app/api/v1/endpoints/users.py": '''"""
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
''',

    "backend/app/api/v1/endpoints/projects.py": '''"""
Project Management Endpoints
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List all projects for current user"""
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return projects

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a new project"""
    project = Project(
        **project_in.model_dump(),
        user_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get project by ID"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """Delete project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
''',

    "backend/app/api/v1/endpoints/feedback.py": '''"""
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
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackResponse

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
''',

    "backend/app/api/v1/endpoints/revisions.py": '''"""
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

@router.get("/feedback/{feedback_id}", response_model=List[RevisionResponse])
def list_feedback_revisions(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """List all revisions for a feedback"""
    revisions = db.query(Revision).join(Feedback).filter(
        Revision.feedback_id == feedback_id,
        Feedback.user_id == current_user.id
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
''',

    "backend/app/api/v1/endpoints/notifications.py": '''"""
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
''',
}

def create_file(filepath: str, content: str):
    """Create a file with the given content"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        f.write(content.lstrip())
    
    print(f"✓ Created: {filepath}")

def main():
    """Generate all endpoint files"""
    print("Generating API endpoint files...")
    print("=" * 60)
    
    for filepath, content in ENDPOINTS.items():
        create_file(filepath, content)
    
    print("=" * 60)
    print(f"✓ Successfully created {len(ENDPOINTS)} endpoint files!")

if __name__ == "__main__":
    main()
