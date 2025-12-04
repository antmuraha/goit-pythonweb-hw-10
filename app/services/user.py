"""Service layer for user authentication and management."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import create_user, get_user_by_email, get_user_by_id, verify_user_email
from app.schemas.user import UserCreate
from app.models.user import User
from app.services.email import send_verification_email
from app.utils.auth import (
    create_access_token,
    create_email_verification_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_email_token,
)


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Register a new user.
    
    Args:
        db: Database session
        user_data: User registration data
        
    Returns:
        User: The created user
        
    Raises:
        ValueError: If user with this email already exists
    """
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("user_already_exists")
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create the user
    user = await create_user(db, email=user_data.email, hashed_password=hashed_password)
    
    # Send verification email
    verification_token = create_email_verification_token(user.email)
    await send_verification_email(user.email, verification_token)
    
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User's email
        password: User's plain text password
        
    Returns:
        Optional[User]: The authenticated user if credentials are valid, None otherwise
    """
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_tokens_for_user(user: User) -> dict:
    """
    Create access and refresh tokens for a user.
    
    Args:
        user: User instance
        
    Returns:
        dict: Dictionary with access_token, refresh_token, and token_type
    """
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def verify_email_service(db: AsyncSession, token: str) -> Optional[User]:
    """
    Verify a user's email using a verification token.
    
    Args:
        db: Database session
        token: Email verification token
        
    Returns:
        Optional[User]: The verified user if token is valid, None otherwise
    """
    email = verify_email_token(token)
    if not email:
        return None
    
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    if user.is_verified:
        return user
    
    return await verify_user_email(db, user.id)
