from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.contact import (
    create_contact,
    get_contact_by_id,
    get_contact_by_email,
    get_contacts,
    search_contacts,
    get_upcoming_birthdays,
    update_contact,
    delete_contact,
)
from app.schemas.contact import ContactCreate, ContactUpdate, ContactRead


async def create_contact_service(
    db: AsyncSession, contact_in: ContactCreate, user_id: int
) -> ContactRead:
    # Avoid duplicate emails within user's contacts
    existing = await get_contact_by_email(db, contact_in.email, user_id)
    if existing:
        raise ValueError("contact_exists")
    return await create_contact(
        db,
        user_id=user_id,
        first_name=contact_in.first_name,
        last_name=contact_in.last_name,
        email=contact_in.email,
        phone_number=contact_in.phone_number,
        birthday=contact_in.birthday,
        additional_data=contact_in.additional_data,
    )


async def list_contacts_service(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    upcoming: bool = False,
) -> List[ContactRead]:
    """List contacts with optional filtering by first_name, last_name or email.

    If `upcoming` is True, returns contacts with birthdays in the next 7 days.
    """
    if upcoming:
        return await get_upcoming_birthdays(db, user_id=user_id, days=7)

    # If any filter present, use the search helper (partial, case-insensitive).
    if first_name or last_name or email:
        return await search_contacts(
            db,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            skip=skip,
            limit=limit,
        )

    return await get_contacts(db, user_id=user_id, skip=skip, limit=limit)


async def get_upcoming_birthdays_service(db: AsyncSession, user_id: int, days: int = 7):
    return await get_upcoming_birthdays(db, user_id=user_id, days=days)


async def get_contact_service(db: AsyncSession, contact_id: int, user_id: int):
    return await get_contact_by_id(db, contact_id, user_id)


async def update_contact_service(
    db: AsyncSession, contact_id: int, contact_in: ContactUpdate, user_id: int
):
    contact = await get_contact_by_id(db, contact_id, user_id)
    if not contact:
        return None
    fields = contact_in.model_dump()
    return await update_contact(db, contact, **fields)


async def delete_contact_service(db: AsyncSession, contact_id: int, user_id: int) -> bool:
    contact = await get_contact_by_id(db, contact_id, user_id)
    if not contact:
        return False
    await delete_contact(db, contact)
    return True
