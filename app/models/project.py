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

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)
    technologies = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_wib_time)
