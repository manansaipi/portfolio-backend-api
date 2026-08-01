from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import re
import cloudinary.uploader

from . import models, schemas
from app.core import database
from app.core.auth import get_current_admin

router = APIRouter(
    prefix="/api/gallery",
    tags=["gallery"]
)

# Valid categories for the museum
VALID_CATEGORIES = [
    "nature", "street", "travel", "portrait",
    "wildlife", "architecture", "video", "featured"
]

def delete_image_from_storage(url: str):
    if not url:
        return
    
    if "/static/img/uploads/" in url:
        match = re.search(r'/static/img/uploads/.*', url)
        if match:
            filepath = match.group(0).lstrip("/")
            if os.path.exists(filepath) and os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Failed to delete local file {filepath}: {e}")
                
    elif "res.cloudinary.com" in url:
        match = re.search(r'/upload/(?:v\d+/)?((?:portfolio_uploads|scrapbook_uploads)/[^.]+)', url)
        if match:
            public_id = match.group(1)
            try:
                if os.getenv("CLOUDINARY_URL"):
                    cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Failed to delete cloudinary file {public_id}: {e}")

@router.post("/", response_model=schemas.GalleryMedia, status_code=status.HTTP_201_CREATED)
def create_media(media: schemas.GalleryMediaCreate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_media = models.GalleryMedia(**media.model_dump())
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

@router.get("/", response_model=List[schemas.GalleryMedia])
def get_all_media(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = Query(None, description="Filter by category"),
    featured: Optional[bool] = Query(None, description="Filter featured items"),
    include_hidden: Optional[bool] = Query(False, description="Include hidden items"),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.GalleryMedia)
    
    # Apply category filter
    if category:
        query = query.filter(models.GalleryMedia.category == category)
    
    # Apply featured filter
    if featured is not None:
        query = query.filter(models.GalleryMedia.is_featured == featured)
        
    # Apply hidden filter
    if not include_hidden:
        query = query.filter(models.GalleryMedia.is_visible == True)
    
    # Order by order asc (nulls last), then created_at desc
    media_list = query.order_by(
        models.GalleryMedia.order.is_(None), 
        models.GalleryMedia.order.asc(), 
        models.GalleryMedia.created_at.desc()
    ).offset(skip).limit(limit).all()
    return media_list

@router.get("/categories", response_model=List[schemas.GalleryCategory])
def get_categories(db: Session = Depends(database.get_db)):
    """Return the list of valid gallery categories from the DB. Seeds defaults if empty."""
    categories = db.query(models.GalleryCategory).all()
    if not categories:
        default_categories = [
            {"slug": "nature", "label": "Nature Hall"},
            {"slug": "street", "label": "Street Hall"},
            {"slug": "travel", "label": "Travel Hall"},
            {"slug": "portrait", "label": "Portrait Hall"}
        ]
        for cat_data in default_categories:
            cat = models.GalleryCategory(**cat_data)
            db.add(cat)
        db.commit()
        categories = db.query(models.GalleryCategory).all()
    return categories

@router.put("/categories/{slug}", response_model=schemas.GalleryCategory)
def update_category(slug: str, cat_update: schemas.GalleryCategoryUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    """Update a category's display label."""
    category = db.query(models.GalleryCategory).filter(models.GalleryCategory.slug == slug).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.label = cat_update.label
    db.commit()
    db.refresh(category)
    return category
@router.put("/reorder", status_code=status.HTTP_200_OK)
def reorder_media(
    items: List[dict],
    db: Session = Depends(database.get_db),
    current_user: str = Depends(get_current_admin)
):
    """Bulk update the order of gallery items. Expects [{id: str, order: int}, ...]"""
    for item in items:
        media_id = item.get("id")
        new_order = item.get("order")
        if media_id is not None and new_order is not None:
            db_media = db.query(models.GalleryMedia).filter(
                models.GalleryMedia.id == media_id
            ).first()
            if db_media:
                db_media.order = new_order
    db.commit()
    return {"message": f"Reordered {len(items)} items"}

@router.put("/{media_id}", response_model=schemas.GalleryMedia)
def update_media(media_id: str, media_update: schemas.GalleryMediaUpdate, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_media = db.query(models.GalleryMedia).filter(models.GalleryMedia.id == media_id).first()
    if not db_media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    old_url = db_media.url
    
    update_data = media_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_media, key, value)
        
    db.commit()
    db.refresh(db_media)
    
    if old_url and old_url != db_media.url:
        delete_image_from_storage(old_url)
        
    return db_media

@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(media_id: str, db: Session = Depends(database.get_db), current_user: str = Depends(get_current_admin)):
    db_media = db.query(models.GalleryMedia).filter(models.GalleryMedia.id == media_id).first()
    if not db_media:
        raise HTTPException(status_code=404, detail="Media not found")
        
    old_url = db_media.url
    
    db.delete(db_media)
    db.commit()
    
    if old_url:
        delete_image_from_storage(old_url)
        
    return None
