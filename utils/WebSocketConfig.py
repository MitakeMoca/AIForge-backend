from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List

app = FastAPI()

# 用于保存所有 WebSocket 连接的列表
active_connections: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 允许指定的来源（对应 Spring 中的 .setAllowedOrigins）
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            print(f"Received message: {data}")

            # 广播消息给所有连接的客户端
            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(f"Message from another user: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("Client disconnected")


# 测试路由，确保 FastAPI 启动正常
@app.get("/")
async def read_root():
    return {"message": "FastAPI WebSocket server is running."}
