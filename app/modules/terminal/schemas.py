from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# --- Terminal Log Schemas ---
class TerminalLogCreate(BaseModel):
    input_text: str
    is_ai_mode: bool = False
    response_text: Optional[str] = None
    execution_time_ms: Optional[int] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    language: Optional[str] = None
    referrer: Optional[str] = None
    audio_base64: Optional[str] = None

class TerminalLogResponse(BaseModel):
    id: str
    input_text: str
    is_ai_mode: bool
    response_text: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    execution_time_ms: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    language: Optional[str] = None
    referrer: Optional[str] = None
    audio_base64: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DeleteLogsRequest(BaseModel):
    log_ids: List[str]

class TerminalLogPaginatedResponse(BaseModel):
    total: int
    items: List[TerminalLogResponse]

class AIRequest(BaseModel):
    question: str
