from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sqlalchemy
from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

def get_wib_time():
    return datetime.now(ZoneInfo("Asia/Jakarta"))

def generate_uuid():
    return str(uuid.uuid4())

from app.core.database import Base

class Writing(Base):
    __tablename__ = "writings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), default=get_wib_time)
    author = Column(String(255), nullable=True)
    author_img = Column(String(255), nullable=True)
    image = Column(String(500), nullable=True)
    images = Column(Text, nullable=True) # Stored as JSON string
    order = Column(Integer, nullable=True)
    
    comments = relationship("Comment", back_populates="writing", cascade="all, delete-orphan")
