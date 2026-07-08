from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.core import database
from app.core.auth import get_current_admin

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"]
)

@router.post("/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[schemas.Project])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Project).offset(skip).limit(limit).all()
