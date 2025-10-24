"""
Pydantic Schemas
Request and response validation schemas
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserInDB,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackResponse,
    FeedbackWithActions,
)
from app.schemas.revision import (
    RevisionCreate,
    RevisionUpdate,
    RevisionResponse,
)
from app.schemas.action_item import (
    ActionItemCreate,
    ActionItemUpdate,
    ActionItemResponse,
)
from app.schemas.notification import (
    NotificationResponse,
    NotificationUpdate,
)
from app.schemas.token import (
    Token,
    TokenPayload,
    LoginRequest,
)

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    # Project
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    # Feedback
    "FeedbackCreate",
    "FeedbackUpdate",
    "FeedbackResponse",
    "FeedbackWithActions",
    # Revision
    "RevisionCreate",
    "RevisionUpdate",
    "RevisionResponse",
    # Action Item
    "ActionItemCreate",
    "ActionItemUpdate",
    "ActionItemResponse",
    # Notification
    "NotificationResponse",
    "NotificationUpdate",
    # Token
    "Token",
    "TokenPayload",
    "LoginRequest",
]
