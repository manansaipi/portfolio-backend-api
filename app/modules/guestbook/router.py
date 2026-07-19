from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_admin
from app.modules.guestbook.models import Guestbook
from app.modules.guestbook.schemas import GuestbookCreate, GuestbookResponse, GuestbookUpdate

router = APIRouter()

@router.get("/", response_model=List[GuestbookResponse])
def read_guestbook(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve guestbook entries.
    """
    entries = db.query(Guestbook).order_by(Guestbook.created_at.desc()).offset(skip).limit(limit).all()
    return entries

@router.post("/", response_model=GuestbookResponse)
def create_guestbook(
    *,
    db: Session = Depends(get_db),
    guestbook_in: GuestbookCreate
):
    """
    Create new guestbook entry.
    """
    entry = Guestbook(
        name=guestbook_in.name,
        message=guestbook_in.message
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.put("/{entry_id}", response_model=GuestbookResponse)
def update_guestbook(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    guestbook_in: GuestbookUpdate,
    current_admin: str = Depends(get_current_admin)
):
    """
    Update a guestbook entry.
    """
    entry = db.query(Guestbook).filter(Guestbook.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Guestbook entry not found")
    
    entry.message = guestbook_in.message
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guestbook(
    *,
    db: Session = Depends(get_db),
    entry_id: int,
    current_admin: str = Depends(get_current_admin)
):
    """
    Delete a guestbook entry.
    """
    entry = db.query(Guestbook).filter(Guestbook.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Guestbook entry not found")
    
    db.delete(entry)
    db.commit()
    return None
