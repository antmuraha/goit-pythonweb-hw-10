"""User router for authenticated user operations."""

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/v1", tags=["User"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    Returns HTTP 200 with user data on success, HTTP 401 if not authenticated.
    """
    return current_user
