import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.modules.multiplayer.manager import manager

router = APIRouter()

@router.websocket("/ws/museum/{room_id}")
async def museum_websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str = Query(None)):
    if not client_id:
        client_id = str(uuid.uuid4())[:8]
    
    await manager.connect(websocket, room_id, client_id)
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                event_type = data.get("type")
                if event_type == "join":
                    await manager.handle_join(room_id, client_id, data)
                elif event_type == "move":
                    await manager.handle_move(room_id, client_id, data)
                elif event_type == "chat":
                    await manager.handle_chat(room_id, client_id, data)
                elif event_type == "update_profile":
                    await manager.handle_update_profile(room_id, client_id, data)
                elif event_type == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(room_id, client_id)
        await manager.broadcast_to_room(room_id, {"type": "player_left", "id": client_id}, exclude_client=client_id)
    except Exception as e:
        manager.disconnect(room_id, client_id)
        await manager.broadcast_to_room(room_id, {"type": "player_left", "id": client_id}, exclude_client=client_id)

@router.get("/rooms/{room_id}/count")
def get_room_visitor_count(room_id: str):
    return {
        "room_id": room_id,
        "count": manager.get_room_count(room_id)
    }

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.multiplayer.models import MuseumChatMessage
from app.modules.multiplayer.schemas import PaginatedChatResponse, ChatMessageResponse
from datetime import datetime

@router.get("/chat/{room_id}", response_model=PaginatedChatResponse)
def get_chat_history(room_id: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    # Query database for messages in this room, newest first
    query = db.query(MuseumChatMessage).filter(MuseumChatMessage.room_id == room_id).order_by(MuseumChatMessage.timestamp.desc())
    
    total = query.count()
    messages_db = query.offset(skip).limit(limit).all()
    
    # We want to return them chronologically for the frontend, so reverse the fetched chunk
    messages_db.reverse()
    
    response_messages = []
    for m in messages_db:
        # Convert timestamp float to HH:MM format
        dt = datetime.fromtimestamp(m.timestamp)
        time_str = dt.strftime("%I:%M %p").lstrip("0")
        
        response_messages.append(ChatMessageResponse(
            id=str(m.id),
            senderId=m.sender_id,
            senderName=m.sender_name,
            senderColor=m.sender_color,
            senderIsAdmin=m.is_admin,
            text=m.message,
            timestamp_float=m.timestamp,
            timestamp=time_str
        ))
        
    has_more = (skip + limit) < total
    return PaginatedChatResponse(messages=response_messages, hasMore=has_more, total=total)
