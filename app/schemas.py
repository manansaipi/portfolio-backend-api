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

# --- Certificate Schemas ---
class CertificateBase(BaseModel):
    name: str
    year: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None
    bg_color: Optional[str] = None
    link: Optional[str] = None
    order: Optional[int] = None

class CertificateCreate(CertificateBase):
    pass

class Certificate(CertificateBase):
    id: str

    class Config:
        from_attributes = True

# --- Terminal Log Schemas ---
class TerminalLogCreate(BaseModel):
    input_text: str
    is_ai_mode: bool = False
    response_text: Optional[str] = None
    execution_time_ms: Optional[int] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    language: Optional[str] = None
    referrer: Optional[str] = None

class TerminalLogResponse(BaseModel):
    id: str
    input_text: str
    is_ai_mode: bool
    response_text: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    execution_time_ms: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    language: Optional[str] = None
    referrer: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DeleteLogsRequest(BaseModel):
    log_ids: List[str]

class TerminalLogPaginatedResponse(BaseModel):
    total: int
    items: List[TerminalLogResponse]

