from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# --- Project Schemas ---
class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    technologies: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
