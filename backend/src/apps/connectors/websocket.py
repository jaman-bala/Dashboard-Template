import logging
from typing import List
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect

from src.apps.main import app

# Настройка логирования
logger = logging.getLogger("websocket_manager")
logging.basicConfig(
    filename="log/websocket.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, List[WebSocket]] = {}
        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, chat_id: UUID):
        logger.info(f"New connection request to chat {chat_id}")
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)
        logger.info(f"Client connected to chat {chat_id}: {websocket.client}")

    def disconnect(self, websocket: WebSocket, chat_id: UUID):
        if (
            chat_id in self.active_connections
            and websocket in self.active_connections[chat_id]
        ):
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]
            logger.info(f"Client disconnected from chat {chat_id}: {websocket.client}")
        else:
            logger.warning(
                f"Attempted to disconnect non-existent client from chat {chat_id}"
            )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        logger.info(f"Sending personal message: {message} to {websocket.client}")
        await websocket.send_text(message)

    async def broadcast(self, chat_id: UUID, message: str):
        logger.info(f"Broadcasting message to chat {chat_id}: {message}")
        for connection in self.active_connections.get(chat_id, []):
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: UUID):
    logger.info(f"WebSocket endpoint hit for chat {chat_id}")
    await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from chat {chat_id}: {data}")
            await manager.broadcast(chat_id, f"Chat {chat_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
        logger.info(f"Client disconnected from chat {chat_id}")
    except Exception as e:
        logger.error(f"Unexpected error in chat {chat_id}: {e}")
        await websocket.close()
