from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

from .comment import Comment

# --- Writing Schemas ---
class WritingBase(BaseModel):
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    author_img: Optional[str] = None
    image: Optional[str] = None
    images: Optional[str] = None
    order: Optional[int] = None

class WritingCreate(WritingBase):
    pass

class WritingUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    author_img: Optional[str] = None
    image: Optional[str] = None
    images: Optional[str] = None
    order: Optional[int] = None

class Writing(WritingBase):
    id: str
    published_at: datetime

    class Config:
        from_attributes = True

class WritingWithComments(Writing):
    comments: List[Comment] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
