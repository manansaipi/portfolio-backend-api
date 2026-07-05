from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sqlalchemy
from datetime import datetime
import uuid

from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)
    technologies = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class Writing(Base):
    __tablename__ = "writings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    author = Column(String(255), nullable=True)
    author_img = Column(String(255), nullable=True)
    image = Column(String(500), nullable=True)
    
    comments = relationship("Comment", back_populates="writing", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    writing_id = Column(String(36), ForeignKey("writings.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String(36), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    username = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    profile_img = Column(String(255), nullable=True)
    likes = Column(Integer, default=0)
    is_author = Column(Boolean, default=False)
    
    writing = relationship("Writing", back_populates="comments")
    replies = relationship(
        "Comment", 
        backref=sqlalchemy.orm.backref("parent", remote_side=[id]),
        cascade="all, delete-orphan"
    )

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    year = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    img = Column(String(255), nullable=True)
    bg_color = Column(String(50), nullable=True)
    link = Column(String(500), nullable=True)
