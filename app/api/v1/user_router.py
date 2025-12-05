"""User router for authenticated user operations."""

from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse

limiter = Limiter(key_func=get_remote_address)


router = APIRouter(prefix="/api/v1", tags=["User"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")  # Limit to 5 requests per minute
async def get_current_user_info(
    request: Request,  # Add request parameter
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    Returns HTTP 200 with user data on success, HTTP 401 if not authenticated.
    """
    return current_user
