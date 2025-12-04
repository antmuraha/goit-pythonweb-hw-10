"""Application-wide constants used by models and schemas.

Centralizing column and field size limits here provides a single source
of truth so models and pydantic schemas stay in sync.
"""

import os

# String length limits (database column sizes / pydantic max_length)
FIRST_NAME_MAX_LENGTH = 100
LAST_NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 100
PHONE_NUMBER_MAX_LENGTH = 20
ADDITIONAL_DATA_MAX_LENGTH = 255

# Authentication and JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
JWT_TOKEN_ALGORITHM = os.getenv("JWT_TOKEN_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
OAUTH2_SCHEME_TOKEN_URL = os.getenv("OAUTH2_SCHEME_TOKEN_URL", "/api/v1/auth/login")

# Email configuration
SMTP_LOCAL_DEBUG = os.getenv("SMTP_LOCAL_DEBUG", "False").lower() in ("true", "1", "yes")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@example.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Application")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "True").lower() in ("true", "1", "yes")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")
