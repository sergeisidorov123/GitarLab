import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Управляет WebSocket соединениями"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Подключает нового клиента"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        """Отключает клиента"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected. Total: {len(self.active_connections)}")
    
    async def send_message(self, client_id: str, message: dict):
        """Отправляет сообщение конкретному клиенту"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    def get_active_count(self) -> int:
        """Количество активных соединений"""
        return len(self.active_connections)