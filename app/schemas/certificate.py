from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


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
