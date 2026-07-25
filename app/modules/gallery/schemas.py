from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GalleryMediaBase(BaseModel):
    url: str
    media_type: Optional[str] = "image"
    caption: Optional[str] = None
    order: Optional[int] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date_taken: Optional[str] = None
    camera: Optional[str] = None
    lens: Optional[str] = None
    tags: Optional[str] = None
    is_featured: Optional[bool] = False

class GalleryMediaCreate(GalleryMediaBase):
    pass

class GalleryMediaUpdate(BaseModel):
    url: Optional[str] = None
    media_type: Optional[str] = None
    caption: Optional[str] = None
    order: Optional[int] = None
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    date_taken: Optional[str] = None
    camera: Optional[str] = None
    lens: Optional[str] = None
    tags: Optional[str] = None
    is_featured: Optional[bool] = None

class GalleryMedia(GalleryMediaBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class GalleryCategoryBase(BaseModel):
    slug: str
    label: str

class GalleryCategoryUpdate(BaseModel):
    label: str

class GalleryCategory(GalleryCategoryBase):
    id: int

    class Config:
        from_attributes = True
