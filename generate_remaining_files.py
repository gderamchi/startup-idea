#!/usr/bin/env python3
"""
Script to generate remaining project files
Run this to complete the project scaffolding
"""

import os
from pathlib import Path

# Define all remaining files with their content
FILES = {
    # Schemas
    "backend/app/schemas/project.py": '''"""
Project Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
''',

    "backend/app/schemas/feedback.py": '''"""
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
''',

    "backend/app/schemas/revision.py": '''"""
Revision Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class RevisionBase(BaseModel):
    feedback_id: UUID
    notes: Optional[str] = None

class RevisionCreate(RevisionBase):
    pass

class RevisionUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class RevisionResponse(RevisionBase):
    id: UUID
    version: int
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
''',

    "backend/app/schemas/action_item.py": '''"""
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
''',

    "backend/app/schemas/notification.py": '''"""
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
''',

    # API Dependencies
    "backend/app/api/deps.py": '''"""
API Dependencies
FastAPI dependency injection for auth, database, etc.
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.core.security import decode_token, verify_token_type
from app.db.session import SessionLocal
from app.models.user import User

security = HTTPBearer()

def get_db() -> Generator:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        verify_token_type(payload, "access")
        user_id: UUID = UUID(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
''',

    # API Router
    "backend/app/api/__init__.py": '"""API package"""',
    "backend/app/api/v1/__init__.py": '"""API v1 package"""',
    "backend/app/api/v1/endpoints/__init__.py": '"""API endpoints"""',
    
    "backend/app/api/v1/api.py": '''"""
API Router
Aggregates all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, projects, feedback, revisions, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(revisions.router, prefix="/revisions", tags=["Revisions"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
''',

    # Alembic
    "backend/alembic.ini": '''[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
''',

    "backend/alembic/env.py": '''"""Alembic environment configuration"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.session import Base
from app.models import *

config = context.config
config.set_main_option("sqlalchemy.url", settings.get_database_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
''',

    "backend/alembic/script.py.mako": '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
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
    """Generate all files"""
    print("Generating remaining project files...")
    print("=" * 60)
    
    for filepath, content in FILES.items():
        create_file(filepath, content)
    
    print("=" * 60)
    print(f"✓ Successfully created {len(FILES)} files!")
    print("\nNext steps:")
    print("1. Run: cd backend && python -m venv venv")
    print("2. Run: source venv/bin/activate")
    print("3. Run: pip install -r requirements.txt")
    print("4. Run: alembic revision --autogenerate -m 'Initial migration'")
    print("5. Run: alembic upgrade head")

if __name__ == "__main__":
    main()
