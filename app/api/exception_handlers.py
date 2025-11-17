from fastapi import Request
from fastapi.responses import JSONResponse


def _is_truncation_error(exc: Exception) -> bool:
    """Return True when the DB exception is a string truncation from asyncpg.

    We avoid importing asyncpg directly so this remains lightweight. SQLAlchemy
    will wrap the DB exception in DBAPIError and expose the original via
    the `orig` attribute; looking at the exception class name is sufficient.
    """
    orig = getattr(exc, "orig", None)
    if orig is None:
        return False
    cls_name = getattr(orig, "__class__", type(orig)).__name__
    return (
        "StringDataRightTruncationError" in cls_name
        or "StringDataRightTruncationError" in str(orig)
    )


async def dbapi_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI exception handler for SQLAlchemy DBAPIError.

    - If the underlying DB exception indicates a string truncation, return
      400 Bad Request with a helpful message.
    - For other DB errors, return 500 Internal Server Error with a generic
      message (avoid exposing DB internals).
    """
    try:
        if _is_truncation_error(exc):
            return JSONResponse(
                status_code=400,
                content={
                    "detail": (
                        "One or more string fields exceed the allowed length for the "
                        "database column. Shorten the value(s) and try again."
                    )
                },
            )
    except Exception:
        # Never raise from the error handler - fall through to generic response
        pass

    return JSONResponse(
        status_code=500,
        content={"detail": "Unexpected database error. Please try again later."},
    )
