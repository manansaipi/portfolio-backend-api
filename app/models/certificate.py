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

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    year = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    img = Column(String(255), nullable=True)
    bg_color = Column(String(50), nullable=True)
    link = Column(String(500), nullable=True)
    order = Column(Integer, nullable=True)
