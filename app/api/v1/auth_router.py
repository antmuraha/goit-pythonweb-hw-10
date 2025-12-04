"""Authentication router for user registration and login."""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.get_session import get_session
from app.schemas.user import EmailVerificationRequest, Token, UserCreate, UserResponse
from app.services.user import (
    authenticate_user,
    create_tokens_for_user,
    register_user,
    verify_email_service,
)
from app.utils.auth import create_email_verification_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class OAuth2PasswordRequestFormStrict:
    """Custom OAuth2 password request form with email instead."""

    def __init__(
        self,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
    ):
        self.username = username
        self.password = password
        self.grant_type = "password"


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Register a new user.

    Returns HTTP 201 on success, HTTP 409 if user already exists.
    """
    try:
        user = await register_user(db, user_data)
        return user
    except ValueError as e:
        if str(e) == "user_already_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        raise


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestFormStrict = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    Authenticate user and return access tokens.

    Accepts username (email) and password in form data.
    Returns HTTP 200 with tokens on success, HTTP 401 if credentials are invalid.
    """
    user = await authenticate_user(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = await create_tokens_for_user(user)
    return tokens


@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str, db: AsyncSession = Depends(get_session)
):
    """
    Verify user's email address using verification token.

    Returns HTTP 200 on success, HTTP 400 if token is invalid.
    """
    user = await verify_email_service(db, token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    return {"message": "Email verified successfully"}


@router.post("/request-email-verification", status_code=status.HTTP_200_OK)
async def request_email_verification(
    email: str, db: AsyncSession = Depends(get_session)
):
    """
    Request a new email verification token.

    This endpoint generates a verification token and sends it to the user's email.
    """
    from app.crud.user import get_user_by_email
    from app.services.email import send_verification_email

    user = await get_user_by_email(db, email)
    if not user:
        # Don't reveal whether user exists or not
        return {"message": "If the email exists, a verification link has been sent"}

    if user.is_verified:
        return {"message": "Email is already verified"}

    verification_token = create_email_verification_token(user.email)
    await send_verification_email(user.email, verification_token)

    return {"message": "Verification link has been sent to your email"}
