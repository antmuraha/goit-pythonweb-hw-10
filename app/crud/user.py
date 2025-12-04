"""CRUD operations for User model."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(db: AsyncSession, email: str, hashed_password: str) -> User:
    """
    Create a new user in the database.
    
    Args:
        db: Database session
        email: User's email address
        hashed_password: User's hashed password
        
    Returns:
        User: The created user instance
    """
    user = User(email=email, hashed_password=hashed_password, is_verified=False, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Retrieve a user by email address.
    
    Args:
        db: Database session
        email: User's email address
        
    Returns:
        Optional[User]: The user if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Retrieve a user by ID.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        Optional[User]: The user if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def verify_user_email(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Mark a user's email as verified.
    
    Args:
        db: Database session
        user_id: User's ID
        
    Returns:
        Optional[User]: The updated user if found, None otherwise
    """
    user = await get_user_by_id(db, user_id)
    if user:
        user.is_verified = True
        await db.commit()
        await db.refresh(user)
    return user


async def update_user_active_status(db: AsyncSession, user_id: int, is_active: bool) -> Optional[User]:
    """
    Update a user's active status.
    
    Args:
        db: Database session
        user_id: User's ID
        is_active: New active status
        
    Returns:
        Optional[User]: The updated user if found, None otherwise
    """
    user = await get_user_by_id(db, user_id)
    if user:
        user.is_active = is_active
        await db.commit()
        await db.refresh(user)
    return user
