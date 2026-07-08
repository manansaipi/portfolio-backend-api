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

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    writing_id = Column(String(36), ForeignKey("writings.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String(36), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    username = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_wib_time)
    profile_img = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    is_author = Column(Boolean, default=False)
    
    writing = relationship("Writing", back_populates="comments")
    replies = relationship(
        "Comment", 
        backref=sqlalchemy.orm.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )
