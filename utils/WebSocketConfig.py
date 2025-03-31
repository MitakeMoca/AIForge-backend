from fastapi import WebSocket
from typing import Dict, List
import asyncio

active_connections = {
    "topic": [],
    "queue": []
}


class WebSocketConfig:

    @staticmethod
    async def connect(websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in active_connections:
            active_connections[channel] = []
        active_connections[channel].append(websocket)

    @staticmethod
    def disconnect(websocket: WebSocket, channel: str):
        if channel in active_connections and websocket in active_connections[channel]:
            active_connections[channel].remove(websocket)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    @staticmethod
    async def broadcast(message: str, channel: str = "topic"):
        connections = active_connections.get(channel, [])
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                # 可以做断线处理
                pass
