from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database

router = APIRouter(
    prefix="/api/experiences",
    tags=["experiences"]
)

@router.post("/", response_model=schemas.Experience, status_code=status.HTTP_201_CREATED)
def create_experience(experience: schemas.ExperienceCreate, db: Session = Depends(database.get_db)):
    db_experience = models.Experience(**experience.model_dump())
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

@router.get("/", response_model=List[schemas.Experience])
def get_experiences(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Experience).order_by(models.Experience.start_date.desc()).offset(skip).limit(limit).all()

@router.put("/{experience_id}", response_model=schemas.Experience)
def update_experience(experience_id: str, experience_update: schemas.ExperienceUpdate, db: Session = Depends(database.get_db)):
    db_experience = db.query(models.Experience).filter(models.Experience.id == experience_id).first()
    if not db_experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    update_data = experience_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_experience, key, value)
    
    db.commit()
    db.refresh(db_experience)
    return db_experience
