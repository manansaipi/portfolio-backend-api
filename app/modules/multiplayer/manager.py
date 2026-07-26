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
        chat_payload = {
            "type": "player_chat",
            "id": client_id,
            "name": player.get("name", "Visitor"),
            "color": player.get("color", "#38bdf8"),
            "message": message_text,
            "timestamp": time.time()
        }

        # Broadcast chat to EVERYONE in the room including sender
        await self.broadcast_to_room(room_id, chat_payload)

    async def handle_update_profile(self, room_id: str, client_id: str, data: Dict[str, Any]):
        if room_id not in self.players or client_id not in self.players[room_id]:
            return

        if "name" in data:
            self.players[room_id][client_id]["name"] = data["name"]
        if "color" in data:
            self.players[room_id][client_id]["color"] = data["color"]

        # Broadcast profile update
        await self.broadcast_to_room(
            room_id,
            {
                "type": "player_updated",
                "id": client_id,
                "name": self.players[room_id][client_id]["name"],
                "color": self.players[room_id][client_id]["color"]
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
            self.disconnect(room_id, cid)
            await self.broadcast_to_room(room_id, {"type": "player_left", "id": cid}, exclude_client=cid)

    def get_room_count(self, room_id: str) -> int:
        return len(self.players.get(room_id, {}))

manager = ConnectionManager()
