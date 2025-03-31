import json
from typing import List

from fastapi import FastAPI, WebSocket, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from config.settings import TORTOISE_ORM
from routers.user import user
from routers.hypara import hypara
from routers.model import model_service
from routers.dataset import dataset
from routers.pic import pic
from routers.tags import tag
from routers.project import project
from routers.favor import favors
from utils.WebSocketConfig import WebSocketConfig

app = FastAPI()
app.include_router(user, prefix='/User', tags=['用户中心'])
app.include_router(hypara, prefix='/Hypara', tags=['超参数管理'])
app.include_router(model_service, prefix='/Model', tags=['模型服务'])
app.include_router(dataset, prefix='/Dataset', tags=['数据集管理'])
app.include_router(pic, prefix='/Pic', tags=['图像管理'])
app.include_router(tag, prefix='/Tags', tags=['标签管理'])
app.include_router(project, prefix='/Project', tags=['项目管理'])
app.include_router(favors, prefix='/Favors', tags=['收藏管理'])

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT"],
    allow_headers=["*"]
)

register_tortoise(
    app=app,
    config=TORTOISE_ORM,
)


# 用于存储已连接的客户端
active_connections: List[WebSocket] = []

# 用于存储每个项目的日志订阅
subscriptions = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    while True:
        data = await websocket.receive_text()  # 接收客户端的消息
        message = json.loads(data)  # 解析 JSON 数据

        # 检查是否是订阅请求
        if message.get("action") == "subscribe":
            channel = message.get("channel")
            if channel:
                project_id = channel.split("_")[-1]  # 从频道名中提取 project_id
                if project_id not in subscriptions:
                    subscriptions[project_id] = []
                subscriptions[project_id].append(websocket)
                data = {
                    "message": f"Subscribed to {channel}"
                }
                await websocket.send_text(json.dumps(data))  # 给客户端发送确认消息

        # 处理其他的消息（例如聊天或日志消息）
        elif message.get("action") == "message":
            # 处理接收到的其他消息
            await websocket.send_text(f"Message received: {message['body']}")


if __name__ == '__main__':
    uvicorn.run('main:app', port=8084, reload=True)
    print("backend start")
