import json
from typing import List

from fastapi import FastAPI, WebSocket, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
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
from utils.WebSocketConfig import active_connections, subscriptions

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


app.mount("/static", StaticFiles(directory="./data/pic"), name="static")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    while True:
        data = await websocket.receive_text()
        message = json.loads(data)

        try:
            if message.get("action") == "subscribe":
                channel = message.get("channel")
                if channel:
                    project_id = channel.split("_")[-1]
                    print(project_id)
                    if project_id not in subscriptions:
                        subscriptions[project_id] = []
                    subscriptions[project_id].append(websocket)

                    await websocket.send_text(json.dumps({
                        "message": f"Subscribed to {channel}"
                    }))
                print(subscriptions)

            elif message.get("action") == "message":
                await websocket.send_text(f"Message received: {message['body']}")
        except WebSocketDisconnect:
            print(f"WebSocket 断开：{websocket.client}")
            if websocket in active_connections:
                active_connections.remove(websocket)


if __name__ == '__main__':
    uvicorn.run('main:app', port=8084, reload=True)
    print("backend start")
