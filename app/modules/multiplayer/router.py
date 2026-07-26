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
                elif event_type == "delete_chat":
                    await manager.handle_delete_chat(room_id, client_id, data)
                elif event_type == "edit_chat":
                    await manager.handle_edit_chat(room_id, client_id, data)
                elif event_type == "update_profile":
                    await manager.handle_update_profile(room_id, client_id, data)
                elif event_type == "ping":
                    await manager.send_personal_message({"type": "pong"}, websocket)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await manager.handle_leave(room_id, client_id)
    except Exception as e:
        await manager.handle_leave(room_id, client_id)

@router.get("/rooms/{room_id}/count")
def get_room_visitor_count(room_id: str):
    return {
        "room_id": room_id,
        "count": manager.get_room_count(room_id)
    }

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.multiplayer.models import MuseumChatMessage
from app.modules.multiplayer.schemas import PaginatedChatResponse, ChatMessageResponse, ChatMessageUpdate, DeleteMessagesRequest
from datetime import datetime

@router.get("/chat/admin/all", response_model=PaginatedChatResponse)
def get_all_chat_admin(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(MuseumChatMessage).order_by(MuseumChatMessage.timestamp.desc())
    total = query.count()
    messages_db = query.offset(skip).limit(limit).all()
    
    response_messages = []
    for m in messages_db:
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
            timestamp=time_str,
            system=(m.sender_id == "SYSTEM")
        ))
    has_more = (skip + limit) < total
    return PaginatedChatResponse(messages=response_messages, hasMore=has_more, total=total)

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
            timestamp=time_str,
            system=(m.sender_id == "SYSTEM")
        ))
        
    has_more = (skip + limit) < total
    return PaginatedChatResponse(messages=response_messages, hasMore=has_more, total=total)

@router.delete("/chat/messages")
async def delete_chat_messages_bulk(payload: DeleteMessagesRequest, db: Session = Depends(get_db)):
    deleted_ids = []
    rooms_affected = set()
    for msg_id in payload.message_ids:
        msg = db.query(MuseumChatMessage).filter(MuseumChatMessage.id == msg_id).first()
        if msg:
            rooms_affected.add(msg.room_id)
            deleted_ids.append(msg_id)
            db.delete(msg)
    db.commit()
    for room_id in rooms_affected:
        for msg_id in deleted_ids:
            await manager.broadcast_to_room(room_id, {"type": "chat_deleted", "id": str(msg_id)})
    return {"status": "success", "deleted_ids": [str(i) for i in deleted_ids]}

@router.delete("/chat/messages/{message_id}")
async def delete_chat_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(MuseumChatMessage).filter(MuseumChatMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    room_id = msg.room_id
    db.delete(msg)
    db.commit()
    await manager.broadcast_to_room(room_id, {"type": "chat_deleted", "id": str(message_id)})
    return {"status": "success", "id": str(message_id)}

@router.put("/chat/messages/{message_id}")
async def update_chat_message(message_id: int, payload: ChatMessageUpdate, db: Session = Depends(get_db)):
    msg = db.query(MuseumChatMessage).filter(MuseumChatMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    room_id = msg.room_id
    msg.message = payload.text
    db.commit()
    db.refresh(msg)
    await manager.broadcast_to_room(room_id, {"type": "chat_edited", "id": str(message_id), "newText": payload.text})
    return {"status": "success", "id": str(message_id), "newText": payload.text}
