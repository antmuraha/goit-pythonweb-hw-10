from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from ..constants import (
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PHONE_NUMBER_MAX_LENGTH,
    ADDITIONAL_DATA_MAX_LENGTH,
)

from ..validators import validate_phone_digits


class ContactBase(BaseModel):
    first_name: str = Field(..., max_length=FIRST_NAME_MAX_LENGTH)
    last_name: str = Field(..., max_length=LAST_NAME_MAX_LENGTH)
    email: EmailStr = Field(..., max_length=EMAIL_MAX_LENGTH)
    phone_number: str = Field(..., max_length=PHONE_NUMBER_MAX_LENGTH)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(None, max_length=ADDITIONAL_DATA_MAX_LENGTH)


class ContactCreate(ContactBase):
    @field_validator("phone_number", mode="before")
    def _validate_phone_number(cls, v):
        return validate_phone_digits(v, allow_none=True)


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=FIRST_NAME_MAX_LENGTH)
    last_name: Optional[str] = Field(None, max_length=LAST_NAME_MAX_LENGTH)
    email: Optional[EmailStr] = Field(None, max_length=EMAIL_MAX_LENGTH)
    phone_number: Optional[str] = Field(None, max_length=PHONE_NUMBER_MAX_LENGTH)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(None, max_length=ADDITIONAL_DATA_MAX_LENGTH)

    @field_validator("phone_number", mode="before")
    def _validate_phone_number(cls, v):
        return validate_phone_digits(v, allow_none=True)


class ContactRead(ContactBase):
    id: int

    model_config = {"from_attributes": True}
