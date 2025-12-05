from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy.exc

from app.api.v1 import auth_router, contact_router, user_router
from app.api.exception_handlers import dbapi_error_handler

app = FastAPI(title="Contact Management API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins. In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Register a global handler for SQLAlchemy DB errors so we can map known DB
# situations (like string truncation) to friendly HTTP responses.
app.add_exception_handler(sqlalchemy.exc.DBAPIError, dbapi_error_handler)

app.include_router(auth_router.router)
app.include_router(contact_router.router)
app.include_router(user_router.router)
