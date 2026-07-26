import json
import time
from typing import Dict, Any, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # room_id -> {client_id: WebSocket}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # room_id -> {client_id: {id, name, color, position, rotation, last_seen}}
        self.players: Dict[str, Dict[str, Dict[str, Any]]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, client_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        if room_id not in self.players:
            self.players[room_id] = {}
        self.active_connections[room_id][client_id] = websocket

    def disconnect(self, room_id: str, client_id: str):
        if room_id in self.active_connections and client_id in self.active_connections[room_id]:
            del self.active_connections[room_id][client_id]
        if room_id in self.players and client_id in self.players[room_id]:
            del self.players[room_id][client_id]

    def _save_system_message(self, room_id: str, message_text: str) -> str:
        from app.core.database import SessionLocal
        from app.modules.multiplayer.models import MuseumChatMessage
        
        db = SessionLocal()
        timestamp = time.time()
        try:
            db_msg = MuseumChatMessage(
                room_id=room_id,
                sender_id="SYSTEM",
                sender_name="System",
                sender_color="#64748b",
                is_admin=False,
                message=message_text,
                timestamp=timestamp
            )
            db.add(db_msg)
            db.commit()
            db.refresh(db_msg)
            return str(db_msg.id)
        except Exception as e:
            print(f"Failed to save system chat message: {e}")
            return f"sys-{timestamp}"
        finally:
            db.close()

    async def handle_leave(self, room_id: str, client_id: str):
        if room_id in self.players and client_id in self.players[room_id]:
            player_name = self.players[room_id][client_id].get("name", "An explorer")
            is_admin = self.players[room_id][client_id].get("isAdmin", False)
            is_admin_activity = is_admin or "admin" in player_name.lower() or "saipi" in player_name.lower()
            if not is_admin_activity:
                self._save_system_message(room_id, f"{player_name} left the museum.")
            self.disconnect(room_id, client_id)
            await self.broadcast_to_room(room_id, {"type": "player_left", "id": client_id, "name": player_name}, exclude_client=client_id)
        else:
            self.disconnect(room_id, client_id)

    async def handle_join(self, room_id: str, client_id: str, data: Dict[str, Any]):
        websocket = self.active_connections.get(room_id, {}).get(client_id)
        if not websocket:
            return

        name = data.get("name", f"Visitor #{client_id[:4]}")
        color = data.get("color", "#38bdf8")
        is_admin = data.get("isAdmin", False)
        position = data.get("position", [0, 2, 0])
        rotation = data.get("rotation", [0, 0, 0])

        player_data = {
            "id": client_id,
            "name": name,
            "color": color,
            "isAdmin": is_admin,
            "position": position,
            "rotation": rotation,
            "last_seen": time.time()
        }
        self.players[room_id][client_id] = player_data

        # 1. Send existing players in the room to the newly joined client
        other_players = [
            p for cid, p in self.players[room_id].items() if cid != client_id
        ]
        await self.send_personal_message({"type": "init", "players": other_players}, websocket)

        # Save join activity to DB unless it is admin activity
        is_admin_activity = is_admin or "admin" in name.lower() or "saipi" in name.lower()
        if not is_admin_activity:
            self._save_system_message(room_id, f"{name} joined the museum.")

        # 2. Broadcast player_joined to all other clients in the room
        await self.broadcast_to_room(room_id, {"type": "player_joined", "player": player_data}, exclude_client=client_id)

    async def handle_move(self, room_id: str, client_id: str, data: Dict[str, Any]):
        if room_id not in self.players or client_id not in self.players[room_id]:
            return

        position = data.get("position")
        rotation = data.get("rotation")
        if position:
            self.players[room_id][client_id]["position"] = position
        if rotation:
            self.players[room_id][client_id]["rotation"] = rotation
        self.players[room_id][client_id]["last_seen"] = time.time()

        # Broadcast player_moved to others
        await self.broadcast_to_room(
            room_id,
            {
                "type": "player_moved",
                "id": client_id,
                "position": self.players[room_id][client_id]["position"],
                "rotation": self.players[room_id][client_id]["rotation"]
            },
            exclude_client=client_id
        )

    async def handle_chat(self, room_id: str, client_id: str, data: Dict[str, Any]):
        if room_id not in self.players or client_id not in self.players[room_id]:
            return
            
        message_text = data.get("message", "").strip()
        if not message_text:
            return

        player = self.players[room_id][client_id]
        timestamp = time.time()
        
        # Save to database
        from app.core.database import SessionLocal
        from app.modules.multiplayer.models import MuseumChatMessage
        
        db = SessionLocal()
        try:
            db_msg = MuseumChatMessage(
                room_id=room_id,
                sender_id=client_id,
                sender_name=player.get("name", "Visitor"),
                sender_color=player.get("color", "#38bdf8"),
                is_admin=player.get("isAdmin", False),
                message=message_text,
                timestamp=timestamp
            )
            db.add(db_msg)
            db.commit()
            db.refresh(db_msg)
            msg_id = str(db_msg.id)
        except Exception as e:
            print(f"Failed to save chat message: {e}")
            msg_id = f"{client_id}-{timestamp}"
        finally:
            db.close()

        chat_payload = {
            "type": "player_chat",
            "id": client_id,
            "db_id": msg_id,
            "name": player.get("name", "Visitor"),
            "color": player.get("color", "#38bdf8"),
            "isAdmin": player.get("isAdmin", False),
            "message": message_text,
            "timestamp": timestamp
        }

        # Broadcast chat to EVERYONE in the room including sender
        await self.broadcast_to_room(room_id, chat_payload)

    async def handle_delete_chat(self, room_id: str, client_id: str, data: Dict[str, Any]):
        if room_id not in self.players or client_id not in self.players[room_id]:
            return
        player = self.players[room_id][client_id]
        if not player.get("isAdmin", False):
            return
            
        msg_id = data.get("msg_id")
        if not msg_id:
            return

        from app.core.database import SessionLocal
        from app.modules.multiplayer.models import MuseumChatMessage
        db = SessionLocal()
        try:
            db.query(MuseumChatMessage).filter(MuseumChatMessage.id == msg_id).delete()
            db.commit()
        except Exception as e:
            print(f"Failed to delete chat: {e}")
        finally:
            db.close()

        await self.broadcast_to_room(room_id, {
            "type": "chat_deleted",
            "msg_id": msg_id
        })

    async def handle_edit_chat(self, room_id: str, client_id: str, data: Dict[str, Any]):
        if room_id not in self.players or client_id not in self.players[room_id]:
            return
        player = self.players[room_id][client_id]
        if not player.get("isAdmin", False):
            return
            
        msg_id = data.get("msg_id")
        new_text = data.get("new_text", "").strip()
        if not msg_id or not new_text:
            return

        from app.core.database import SessionLocal
        from app.modules.multiplayer.models import MuseumChatMessage
        db = SessionLocal()
        try:
            db_msg = db.query(MuseumChatMessage).filter(MuseumChatMessage.id == msg_id).first()
            if db_msg:
                db_msg.message = new_text
                db.commit()
        except Exception as e:
            print(f"Failed to edit chat: {e}")
        finally:
            db.close()

        await self.broadcast_to_room(room_id, {
            "type": "chat_edited",
            "msg_id": msg_id,
            "new_text": new_text
        })

    async def handle_update_profile(self, room_id: str, client_id: str, data: Dict[str, Any]):
        if room_id not in self.players or client_id not in self.players[room_id]:
            return

        old_name = self.players[room_id][client_id]["name"]
        old_color = self.players[room_id][client_id]["color"]
        new_name = data.get("name", old_name)
        new_color = data.get("color", old_color)

        is_admin = self.players[room_id][client_id].get("isAdmin", False)
        is_admin_activity = is_admin or "admin" in new_name.lower() or "saipi" in new_name.lower() or "admin" in old_name.lower() or "saipi" in old_name.lower()

        activity_msgs = []
        if new_name != old_name:
            self.players[room_id][client_id]["name"] = new_name
            msg = f"{old_name} changed nickname to {new_name}."
            if not is_admin_activity:
                self._save_system_message(room_id, msg)
            activity_msgs.append(msg)
        if new_color != old_color:
            self.players[room_id][client_id]["color"] = new_color
            msg = f"{new_name} changed avatar color."
            if not is_admin_activity:
                self._save_system_message(room_id, msg)
            activity_msgs.append(msg)

        # Broadcast profile update
        await self.broadcast_to_room(
            room_id,
            {
                "type": "player_updated",
                "id": client_id,
                "name": self.players[room_id][client_id]["name"],
                "color": self.players[room_id][client_id]["color"],
                "activity": activity_msgs
            }
        )

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            pass

    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_client: str = None):
        if room_id not in self.active_connections:
            return
        msg_str = json.dumps(message)
        dead_clients = []
        for cid, ws in self.active_connections[room_id].items():
            if exclude_client and cid == exclude_client:
                continue
            try:
                await ws.send_text(msg_str)
            except Exception:
                dead_clients.append(cid)

        for cid in dead_clients:
            await self.handle_leave(room_id, cid)

    def get_room_count(self, room_id: str) -> int:
        return len(self.players.get(room_id, {}))

manager = ConnectionManager()
