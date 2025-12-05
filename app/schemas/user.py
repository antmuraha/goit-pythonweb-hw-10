"""Pydantic schemas for user authentication and registration."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """Schema for user registration."""
    
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")


class UserResponse(UserBase):
    """Schema for user response (no password)."""
    
    id: int
    avatar_url: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    
    # TODO ?
    email: Optional[str] = None


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""
    
    token: str = Field(..., description="Email verification token")
