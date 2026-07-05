from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, database
from ..auth import get_current_admin

router = APIRouter(
    prefix="/api/certificates",
    tags=["certificates"]
)

@router.post("/", response_model=schemas.Certificate, status_code=status.HTTP_201_CREATED)
def create_certificate(certificate: schemas.CertificateCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_certificate = models.Certificate(**certificate.model_dump())
    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)
    return db_certificate

@router.get("/", response_model=List[schemas.Certificate])
def get_certificates(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Certificate).order_by(models.Certificate.order.is_(None), models.Certificate.order.asc(), models.Certificate.id.desc()).offset(skip).limit(limit).all()
