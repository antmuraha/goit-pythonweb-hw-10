from fastapi import FastAPI
import sqlalchemy.exc

from app.api.v1 import contact_router
from app.api.exception_handlers import dbapi_error_handler


app = FastAPI(title="Contact Management API", version="1.0.0")

# Register a global handler for SQLAlchemy DB errors so we can map known DB
# situations (like string truncation) to friendly HTTP responses.
app.add_exception_handler(sqlalchemy.exc.DBAPIError, dbapi_error_handler)

app.include_router(contact_router.router)
