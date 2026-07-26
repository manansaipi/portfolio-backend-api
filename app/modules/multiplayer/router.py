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
