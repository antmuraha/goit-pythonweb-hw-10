"""Security utilities for OAuth2 authentication."""

from fastapi.security import OAuth2PasswordBearer
from app.constants import OAUTH2_SCHEME_TOKEN_URL

# OAuth2 scheme for token authentication
# tokenUrl is the endpoint where users can obtain tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=OAUTH2_SCHEME_TOKEN_URL)
