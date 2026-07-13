from pydantic import BaseModel, Field
from datetime import datetime

class GuestbookCreate(BaseModel):
    name: str = Field(..., max_length=100)
    message: str = Field(..., max_length=500)

class GuestbookUpdate(BaseModel):
    message: str = Field(..., max_length=500)

class GuestbookResponse(BaseModel):
    id: int
    name: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
