"""User router for authenticated user operations."""

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import AVATAR_ALLOWED_TYPES, AVATAR_MAX_FILE_SIZE
from app.crud.user import update_avatar
from app.db.get_session import get_session
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.cloudinary import upload_avatar

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


@router.post("/users/avatar", response_model=dict, status_code=status.HTTP_200_OK)
# @limiter.limit("3/minute")  # Limit to 3 requests per minute
async def update_user_avatar(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
):
    """
    Update user avatar by uploading an image to Cloudinary.
    
    Accepts JPEG and PNG images up to 5MB.
    The image will be automatically cropped to 250x250 pixels.
    
    Returns:
        dict: Contains the new avatar URL
        
    Raises:
        HTTPException 400: If file type is not allowed or file size exceeds limit
        HTTPException 500: If upload to Cloudinary fails
    """
    # Validate file type
    if file.content_type not in AVATAR_ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(AVATAR_ALLOWED_TYPES)}",
        )
    
    # Read file content to check size
    file_content = await file.read()
    file_size = len(file_content)
    
    # Validate file size
    if file_size > AVATAR_MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {AVATAR_MAX_FILE_SIZE / (1024 * 1024):.1f}MB",
        )
    
    # Reset file pointer for upload
    await file.seek(0)
    
    # Upload to Cloudinary
    avatar_url = await upload_avatar(file, current_user.id)
    
    # Update user avatar in database
    await update_avatar(db, current_user.id, avatar_url)
    
    return {"avatar_url": avatar_url}
