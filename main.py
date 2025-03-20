from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from config.settings import TORTOISE_ORM
from routers.user import user

app = FastAPI()
app.include_router(user, prefix='/User', tags=['用户中心'])

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


if __name__ == '__main__':
    uvicorn.run('main:app', port=8084, reload=True)
