import os
import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.utils import _str_to_bool

# Read the SQLALCHEMY_DATABASE_URL from environment (use .env in docker-compose)
DEFAULT_DB_URL = (
    "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"
)
raw_db_url = os.environ.get("SQLALCHEMY_DATABASE_URL", DEFAULT_DB_URL)

# If the configured URL uses psycopg2, convert it to asyncpg for async engine
if "psycopg2" in raw_db_url:
    async_db_url = raw_db_url.replace("psycopg2", "asyncpg")
else:
    async_db_url = raw_db_url

# Determine whether to echo SQL from environment variables.
# Supported env vars (checked in order): SQLALCHEMY_ECHO
# Accepts truthy values: 1, true, yes, on (case-insensitive)
_env_val = os.environ.get("SQLALCHEMY_ECHO")
SQL_ECHO = _str_to_bool(_env_val)

# Configure SQL logging to console only when enabled via env var
logging.basicConfig()
sql_logger = logging.getLogger("sqlalchemy.engine")
sql_logger.setLevel(logging.INFO if SQL_ECHO else logging.WARNING)

# Create async engine (SQLAlchemy 2.0 style)
engine: AsyncEngine = create_async_engine(async_db_url, echo=SQL_ECHO, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy Session and ensure it's closed after use.

    Use as a FastAPI dependency: Depends(get_session)
    """
    async with SessionLocal() as session:
        yield session
