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

class TerminalLog(Base):
    __tablename__ = "terminal_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    input_text = Column(Text, nullable=False)
    is_ai_mode = Column(Boolean, default=False)
    response_text = Column(Text, nullable=True)
    ip_address = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True)
    referrer = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_wib_time)
