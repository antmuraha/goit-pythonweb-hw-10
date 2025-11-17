from typing import List, Optional

from datetime import date

from sqlalchemy import select
from sqlalchemy.sql import and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact as ContactModel


async def create_contact(
    db: AsyncSession,
    *,
    first_name: str,
    last_name: str,
    email: str,
    phone_number: str,
    birthday: Optional[str] = None,
    additional_data: Optional[str] = None,
):
    contact = ContactModel(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        birthday=birthday,
        additional_data=additional_data,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contact_by_id(
    db: AsyncSession, contact_id: int
) -> Optional[ContactModel]:
    return await db.get(ContactModel, contact_id)


async def get_contacts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[ContactModel]:
    result = await db.execute(
        select(ContactModel).order_by(ContactModel.id.asc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def search_contacts(
    db: AsyncSession,
    *,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ContactModel]:
    """Search contacts by provided fields (case-insensitive, partial match).

    All provided filters are combined with AND. If no filters provided, returns
    the normal paginated list.
    """
    clauses = []
    if first_name:
        clauses.append(ContactModel.first_name.ilike(f"%{first_name}%"))
    if last_name:
        clauses.append(ContactModel.last_name.ilike(f"%{last_name}%"))
    if email:
        clauses.append(ContactModel.email.ilike(f"%{email}%"))

    if not clauses:
        return await get_contacts(db, skip=skip, limit=limit)

    stmt = (
        select(ContactModel)
        .where(and_(*clauses))
        .order_by(ContactModel.id.asc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_upcoming_birthdays(db: AsyncSession, days: int = 7) -> List[ContactModel]:
    """Return contacts whose birthdays occur within the next `days` days.

    This performs a DB query to fetch contacts with non-null birthdays and
    filters them in Python by computing the next occurrence of their birthday
    (handles year wrap). Results are ordered by how soon the birthday occurs.
    """
    result = await db.execute(
        select(ContactModel).where(ContactModel.birthday.is_not(None))
    )
    contacts = result.scalars().all()
    today = date.today()
    upcoming: List[tuple[int, ContactModel]] = []
    for c in contacts:
        bd = c.birthday
        if not bd:
            continue
        # Next occurrence of birthday (in current year or next year)
        next_bd = bd.replace(year=today.year)
        if next_bd < today:
            next_bd = bd.replace(year=today.year + 1)
        delta = (next_bd - today).days
        if 0 <= delta <= days:
            upcoming.append((delta, c))

    upcoming.sort(key=lambda t: t[0])
    return [c for _d, c in upcoming]


async def get_contact_by_email(db: AsyncSession, email: str) -> Optional[ContactModel]:
    result = await db.execute(select(ContactModel).where(ContactModel.email == email))
    return result.scalars().first()


async def update_contact(
    db: AsyncSession, contact: ContactModel, **fields
) -> ContactModel:
    for key, value in fields.items():
        if value is not None and hasattr(contact, key):
            setattr(contact, key, value)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(db: AsyncSession, contact: ContactModel) -> None:
    await db.delete(contact)
    await db.commit()
