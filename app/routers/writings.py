from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth import get_current_admin

router = APIRouter(
    prefix="/api/writings",
    tags=["writings"]
)

@router.post("/", response_model=schemas.Writing, status_code=status.HTTP_201_CREATED)
def create_writing(writing: schemas.WritingCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_writing = models.Writing(**writing.model_dump())
    db.add(db_writing)
    db.commit()
    db.refresh(db_writing)
    return db_writing

@router.get("/", response_model=List[schemas.Writing])
def get_writings(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Writing).order_by(models.Writing.order.is_(None), models.Writing.order.asc(), models.Writing.published_at.desc()).offset(skip).limit(limit).all()

@router.put("/{writing_id}", response_model=schemas.Writing)
def update_writing(writing_id: str, writing_update: schemas.WritingUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
    
    update_data = writing_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_writing, key, value)
        
    db.commit()
    db.refresh(db_writing)
    return db_writing

@router.delete("/{writing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_writing(writing_id: str, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
        
    db.delete(db_writing)
    db.commit()
    return None

@router.get("/{writing_id}", response_model=schemas.Writing)
def get_writing(writing_id: str, db: Session = Depends(database.get_db)):
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
    return db_writing
