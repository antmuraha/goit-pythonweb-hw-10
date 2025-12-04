"""Authentication utilities for password hashing and JWT token management."""

import base64
import hashlib
import bcrypt
from jose import JWTError, jwt

from datetime import datetime, timedelta, timezone
from typing import Optional


from app.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_TOKEN_ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)


def prehash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA256 to handle bcrypt's 72-byte limit.

    This allows passwords of any length while maintaining security.
    SHA256 produces 32 bytes, base64 encoded to ~44 characters.

    Args:
        password: The plain text password

    Returns:
        bytes: The base64-encoded SHA256 hash as bytes
    """
    # Hash with SHA256 (produces 32 bytes)
    sha_hash = hashlib.sha256(password.encode("utf-8")).digest()
    # Encode to base64 for safe string representation (~44 chars, < 72 bytes)
    return base64.b64encode(sha_hash)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        bool: True if password matches, False otherwise
    """
    # Pre-hash with SHA256 to handle any password length
    prehashed = prehash_password(plain_password)
    return bcrypt.checkpw(prehashed, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """
    Hash a password using SHA256 + bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password
    """
    # Pre-hash with SHA256 to handle any password length
    prehashed = prehash_password(password)
    # Generate salt and hash
    hashed = bcrypt.hashpw(prehashed, bcrypt.gensalt())
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token (typically {"sub": user_email})
        expires_delta: Optional custom expiration time

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_TOKEN_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.

    Args:
        data: The data to encode in the token (typically {"sub": user_email})

    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_TOKEN_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """
    Decode a JWT token and extract the subject (user email).

    Args:
        token: The JWT token to decode

    Returns:
        Optional[str]: The user email from token subject, or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_TOKEN_ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """
    Create a JWT token for email verification.

    Args:
        email: The user's email address

    Returns:
        str: The encoded JWT token for email verification
    """
    data = {"sub": email, "type": "email_verification"}
    expire = datetime.now(timezone.utc) + timedelta(hours=24)  # 24 hour expiration
    data.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(data, SECRET_KEY, algorithm=JWT_TOKEN_ALGORITHM)


def verify_email_token(token: str) -> Optional[str]:
    """
    Verify an email verification token.

    Args:
        token: The JWT token to verify

    Returns:
        Optional[str]: The user email if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_TOKEN_ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None
