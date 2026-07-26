from sqlalchemy import Column, Integer, String, Text, Float, Boolean, Index
from app.core.database import Base
import time

class MuseumChatMessage(Base):
    __tablename__ = "museum_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(50), nullable=False)
    sender_id = Column(String(100), nullable=False)
    sender_name = Column(String(100), nullable=False)
    sender_color = Column(String(20), nullable=False)
    is_admin = Column(Boolean, default=False)
    message = Column(Text, nullable=False)
    timestamp = Column(Float, default=time.time)

    # Index for fast pagination
    __table_args__ = (
        Index("ix_museum_chat_room_time", "room_id", "timestamp"),
    )
