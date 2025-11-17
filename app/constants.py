"""Application-wide constants used by models and schemas.

Centralizing column and field size limits here provides a single source
of truth so models and pydantic schemas stay in sync.
"""

# String length limits (database column sizes / pydantic max_length)
FIRST_NAME_MAX_LENGTH = 100
LAST_NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 100
PHONE_NUMBER_MAX_LENGTH = 20
ADDITIONAL_DATA_MAX_LENGTH = 255
