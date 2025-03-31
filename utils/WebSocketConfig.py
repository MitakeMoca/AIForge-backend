import json
import uuid
from typing import Dict, List
from fastapi import WebSocket

active_connections: List[WebSocket] = []
subscriptions: Dict[str, List[WebSocket]] = {}


async def broadcast_to_project(project_id: int, message: str):
    """
    向某个项目频道的所有订阅者广播消息
    """
    websockets = subscriptions[str(project_id)]
    print(f"subscriptions: {subscriptions} {websockets} {project_id}")
    if websockets is None:
        print(f"[Warning] 没有订阅者，项目 {project_id} 的消息无法广播")
        return
    unique_string = str(uuid.uuid4())
    for ws in websockets:
        try:
            await ws.send_text(json.dumps({"message_id": unique_string, 'message': message, 'type': "log"}))
        except Exception as e:
            print(f"[WebSocket] 发送失败: {e}")
