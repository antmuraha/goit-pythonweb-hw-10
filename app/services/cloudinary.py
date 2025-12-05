"""Cloudinary service for avatar upload and management."""

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.constants import (
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_CLOUD_NAME,
)


def configure_cloudinary() -> None:
    """Configure Cloudinary with credentials from environment variables."""
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )


async def upload_avatar(file: UploadFile, user_id: int) -> str:
    """
    Upload user avatar to Cloudinary.
    
    Args:
        file: The uploaded file object
        user_id: User ID to use in the public_id
        
    Returns:
        str: The secure URL of the uploaded avatar
        
    Raises:
        HTTPException: If upload fails
    """
    configure_cloudinary()
    
    try:
        # Create a unique public_id for the avatar
        public_id = f"avatars/user_{user_id}"
        
        # Upload the file to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            overwrite=True,  # Overwrite existing avatar
            folder="avatars",
            transformation=[
                {"width": 250, "height": 250, "crop": "fill", "gravity": "face"},
            ],
        )
        
        # Return the secure URL
        return upload_result.get("secure_url")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}",
        ) from e
