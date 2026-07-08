from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.core import database
from app.core.auth import get_current_admin

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

@router.put("/{id}", response_model=schemas.Certificate)
def update_certificate(id: str, certificate: schemas.CertificateCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_certificate = db.query(models.Certificate).filter(models.Certificate.id == id).first()
    if not db_certificate:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    for key, value in certificate.model_dump().items():
        setattr(db_certificate, key, value)
    
    db.commit()
    db.refresh(db_certificate)
    return db_certificate

@router.delete("/{id}")
def delete_certificate(id: str, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_certificate = db.query(models.Certificate).filter(models.Certificate.id == id).first()
    if not db_certificate:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    db.delete(db_certificate)
    db.commit()
    return {"message": "Certificate deleted successfully"}
