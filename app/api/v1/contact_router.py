from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.contact import (
    ContactCreate,
    ContactRead,
    ContactUpdate,
)
from app.services.contact import (
    create_contact_service,
    list_contacts_service,
    get_contact_service,
    update_contact_service,
    delete_contact_service,
)
from app.db.get_session import get_session

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact_endpoint(
    contact_in: ContactCreate, db: AsyncSession = Depends(get_session)
):
    try:
        contact = await create_contact_service(db, contact_in)
    except ValueError as exc:
        if str(exc) == "contact_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact with this email already exists",
            )
        raise
    return contact


@router.get("/", response_model=List[ContactRead])
async def list_contacts_endpoint(
    skip: int = 0,
    limit: int = 100,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    upcoming: bool = False,
    db: AsyncSession = Depends(get_session),
):
    """List contacts. Optional query params allow filtering by first_name,
    last_name or email (partial, case-insensitive). Use `upcoming=true` to
    retrieve contacts with birthdays in the next 7 days.
    """
    return await list_contacts_service(
        db,
        skip=skip,
        limit=limit,
        first_name=first_name,
        last_name=last_name,
        email=email,
        upcoming=upcoming,
    )


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact_endpoint(
    contact_id: int, db: AsyncSession = Depends(get_session)
):
    contact = await get_contact_service(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactRead)
async def update_contact_endpoint(
    contact_id: int, contact_in: ContactUpdate, db: AsyncSession = Depends(get_session)
):
    contact = await update_contact_service(db, contact_id, contact_in)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact_endpoint(
    contact_id: int, db: AsyncSession = Depends(get_session)
):
    ok = await delete_contact_service(db, contact_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return None
