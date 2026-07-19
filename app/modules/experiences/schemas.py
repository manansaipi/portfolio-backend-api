from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# --- Experience Schemas ---
class ExperienceBase(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None
    points: Optional[str] = None
    images: Optional[str] = None
    bg_color: Optional[str] = None
    url: Optional[str] = None
    order: Optional[int] = None

class ExperienceCreate(ExperienceBase):
    pass

class ExperienceUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None
    points: Optional[str] = None
    images: Optional[str] = None
    bg_color: Optional[str] = None
    url: Optional[str] = None
    order: Optional[int] = None

class Experience(ExperienceBase):
    id: str

    class Config:
        from_attributes = True
