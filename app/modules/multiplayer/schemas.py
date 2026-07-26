from pydantic import BaseModel
from typing import List, Optional

class ChatMessageResponse(BaseModel):
    id: str  # We will map this as senderId-timestamp or just the db id as string
    senderId: str
    senderName: str
    senderColor: str
    senderIsAdmin: bool
    text: str
    timestamp_float: float
    timestamp: str
    system: Optional[bool] = False

    class Config:
        from_attributes = True

class PaginatedChatResponse(BaseModel):
    messages: List[ChatMessageResponse]
    hasMore: bool
    total: int

class ChatMessageUpdate(BaseModel):
    text: str

class DeleteMessagesRequest(BaseModel):
    message_ids: List[int]
