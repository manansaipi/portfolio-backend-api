from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# --- Comment Schemas ---
class CommentBase(BaseModel):
    username: str
    content: str
    parent_id: Optional[str] = None
    profile_img: Optional[str] = None
    likes: Optional[int] = 0

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    username: Optional[str] = None

class Comment(CommentBase):
    id: str
    writing_id: str
    created_at: datetime
    is_author: bool = False
    
    # We will build a tree recursively
    replies: List["Comment"] = Field(default_factory=list)

    class Config:
        from_attributes = True
