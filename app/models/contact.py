from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..constants import (
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PHONE_NUMBER_MAX_LENGTH,
    ADDITIONAL_DATA_MAX_LENGTH,
)

from .base import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(
        String(FIRST_NAME_MAX_LENGTH), nullable=False
    )
    last_name: Mapped[str] = mapped_column(String(LAST_NAME_MAX_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), nullable=False)
    phone_number: Mapped[str] = mapped_column(
        String(PHONE_NUMBER_MAX_LENGTH), nullable=False
    )
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    additional_data: Mapped[Optional[str]] = mapped_column(
        String(ADDITIONAL_DATA_MAX_LENGTH), nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Relationship to User
    owner: Mapped["User"] = relationship("User", back_populates="contacts")  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<Contact(name='{self.first_name} {self.last_name}', email={self.email})>"
        )
