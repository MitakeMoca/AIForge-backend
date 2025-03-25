from fastapi import FastAPI
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

app = FastAPI()
app.include_router(user, prefix='/User', tags=['用户中心'])
app.include_router(hypara, prefix='/Hypara', tags=['超参数管理'])
app.include_router(model_service, prefix='/Model', tags=['模型服务'])
app.include_router(dataset, prefix='/Dataset', tags=['数据集管理'])
app.include_router(pic, prefix='/Pic', tags=['图像管理'])
app.include_router(tag, prefix='/Tags', tags=['标签管理'])
app.include_router(project, prefix='/Project', tags=['项目管理'])


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
