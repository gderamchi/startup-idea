"""
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
