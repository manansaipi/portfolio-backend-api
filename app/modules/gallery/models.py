from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

def get_wib_time():
    return datetime.now(ZoneInfo("Asia/Jakarta"))

def generate_uuid():
    return str(uuid.uuid4())

from app.core.database import Base

class GalleryMedia(Base):
    __tablename__ = "gallery_media"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    url = Column(String(500), nullable=False)
    media_type = Column(String(50), nullable=False, default="image") # 'image' or 'video'
    caption = Column(String(500), nullable=True)
    order = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=get_wib_time, index=True)
    
    # New fields for museum gallery management
    category = Column(String(50), nullable=True, index=True)  # nature, street, travel, portrait, wildlife, architecture, video, featured
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    date_taken = Column(String(50), nullable=True)
    camera = Column(String(100), nullable=True)
    lens = Column(String(100), nullable=True)
    tags = Column(String(500), nullable=True)  # comma-separated
    is_featured = Column(Boolean, nullable=True, default=False)
    is_visible = Column(Boolean, nullable=True, default=True)

class GalleryCategory(Base):
    __tablename__ = "gallery_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, index=True) # nature, street, travel, portrait
    label = Column(String(100), nullable=False) # e.g. "Nature Hall"
