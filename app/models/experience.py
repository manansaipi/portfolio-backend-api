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

class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    img = Column(String(255), nullable=True)
    points = Column(Text, nullable=True) # Stored as JSON string
    images = Column(Text, nullable=True) # Stored as JSON string
    bg_color = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)
    order = Column(Integer, nullable=True)
