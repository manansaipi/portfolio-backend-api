from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time
from app import models, schemas
from app.core import database
from app.core.auth import get_current_admin

router = APIRouter(
    prefix="/api/experiences",
    tags=["experiences"]
)

EXPERIENCES_CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 1800  # 30 minutes

def clear_experiences_cache():
    EXPERIENCES_CACHE["data"] = None

@router.post("/", response_model=schemas.Experience, status_code=status.HTTP_201_CREATED)
def create_experience(experience: schemas.ExperienceCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_experience = models.Experience(**experience.model_dump())
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    clear_experiences_cache()
    return db_experience

@router.get("/", response_model=List[schemas.Experience])
def get_experiences(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    now = time.time()
    if skip == 0 and limit == 100 and EXPERIENCES_CACHE["data"] is not None and now - EXPERIENCES_CACHE["timestamp"] < CACHE_TTL:
        return EXPERIENCES_CACHE["data"]
        
    experiences = db.query(models.Experience).order_by(models.Experience.order.is_(None), models.Experience.order.asc(), models.Experience.start_date.desc()).offset(skip).limit(limit).all()
    
    if skip == 0 and limit == 100:
        pydantic_exp = [schemas.Experience.model_validate(e) for e in experiences]
        EXPERIENCES_CACHE["data"] = pydantic_exp
        EXPERIENCES_CACHE["timestamp"] = now
    
    return experiences

@router.put("/{experience_id}", response_model=schemas.Experience)
def update_experience(experience_id: str, experience_update: schemas.ExperienceUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_experience = db.query(models.Experience).filter(models.Experience.id == experience_id).first()
    if not db_experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    
    update_data = experience_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_experience, key, value)
    
    db.commit()
    db.refresh(db_experience)
    clear_experiences_cache()
    return db_experience

@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(experience_id: str, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_experience = db.query(models.Experience).filter(models.Experience.id == experience_id).first()
    if not db_experience:
        raise HTTPException(status_code=404, detail="Experience not found")
        
    db.delete(db_experience)
    db.commit()
    return None
