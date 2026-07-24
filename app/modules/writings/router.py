from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time
from . import models, schemas
from app.core import database
from app.core.auth import get_current_admin

router = APIRouter(
    prefix="/api/writings",
    tags=["writings"]
)

WRITINGS_CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 1800  # 30 minutes

import os
import re
import cloudinary.uploader

def delete_image_from_storage(url: str):
    if not url:
        return
    if "/static/img/uploads/" in url:
        # Local file
        match = re.search(r'/static/img/uploads/.*', url)
        if match:
            filepath = match.group(0).lstrip("/")
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Failed to delete local file {filepath}: {e}")
                
    elif "res.cloudinary.com" in url:
        # Cloudinary file
        match = re.search(r'/upload/(?:v\d+/)?(portfolio_uploads/[^.]+)', url)
        if match:
            public_id = match.group(1)
            try:
                if os.getenv("CLOUDINARY_URL"):
                    cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Failed to delete cloudinary file {public_id}: {e}")

import json

def get_images_from_content(html_content: str):
    if not html_content:
        return []
    return re.findall(r'<img[^>]+src="([^">]+)"', html_content)

def clear_writings_cache():
    WRITINGS_CACHE["data"] = None

@router.post("/", response_model=schemas.Writing, status_code=status.HTTP_201_CREATED)
def create_writing(writing: schemas.WritingCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_writing = models.Writing(**writing.model_dump())
    db.add(db_writing)
    db.commit()
    db.refresh(db_writing)
    clear_writings_cache()
    return db_writing

@router.get("/", response_model=List[schemas.Writing])
def get_writings(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    now = time.time()
    # if skip == 0 and limit == 100 and WRITINGS_CACHE["data"] is not None and now - WRITINGS_CACHE["timestamp"] < CACHE_TTL:
    #     return WRITINGS_CACHE["data"]
        
    writings = db.query(models.Writing).order_by(models.Writing.order.is_(None), models.Writing.order.asc(), models.Writing.published_at.desc()).offset(skip).limit(limit).all()
    
    if skip == 0 and limit == 100:
        pydantic_writings = [schemas.Writing.model_validate(w) for w in writings]
        WRITINGS_CACHE["data"] = pydantic_writings
        WRITINGS_CACHE["timestamp"] = now
        
    return writings

@router.put("/{writing_id}", response_model=schemas.Writing)
def update_writing(writing_id: str, writing_update: schemas.WritingUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
    
    old_image = db_writing.image
    old_images_json = db_writing.images
    old_content = db_writing.content
    
    update_data = writing_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_writing, key, value)
        
    db.commit()
    db.refresh(db_writing)
    
    if old_image and old_image != db_writing.image:
        delete_image_from_storage(old_image)
        
    try:
        old_carousel = json.loads(old_images_json) if old_images_json else []
    except:
        old_carousel = []
        
    try:
        new_carousel = json.loads(db_writing.images) if db_writing.images else []
    except:
        new_carousel = []
        
    for img in old_carousel:
        if img not in new_carousel:
            delete_image_from_storage(img)
            
    old_content_imgs = get_images_from_content(old_content)
    new_content_imgs = get_images_from_content(db_writing.content)
    
    for img in old_content_imgs:
        if img not in new_content_imgs:
            delete_image_from_storage(img)
        
    clear_writings_cache()
    return db_writing

@router.delete("/{writing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_writing(writing_id: str, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
    old_image = db_writing.image
    old_images_json = db_writing.images
    old_content = db_writing.content
        
    db.delete(db_writing)
    db.commit()
    
    if old_image:
        delete_image_from_storage(old_image)
        
    try:
        old_carousel = json.loads(old_images_json) if old_images_json else []
    except:
        old_carousel = []
    for img in old_carousel:
        delete_image_from_storage(img)
        
    old_content_imgs = get_images_from_content(old_content)
    for img in old_content_imgs:
        delete_image_from_storage(img)
        
    clear_writings_cache()
    return None

@router.get("/{writing_id}", response_model=schemas.Writing)
def get_writing(writing_id: str, db: Session = Depends(database.get_db)):
    db_writing = db.query(models.Writing).filter(models.Writing.id == writing_id).first()
    if not db_writing:
        raise HTTPException(status_code=404, detail="Writing not found")
    return db_writing
