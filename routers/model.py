from typing import Optional

from fastapi import APIRouter, Form, UploadFile, File
from pydantic import BaseModel

from models.model import Model
from services.model import add_model_service
from utils.ResultGenerator import ResultGenerator

model_service = APIRouter()


class ModelIn(BaseModel):
    modelName: str
    modelDescription: str
    modelOverviewMarkdown: str
    modelFrame: str
    imageId: int
    userId: str
    isPublic: int
    hyparaPath: str
    tag: str


@model_service.put('/')
async def add_model(
        model_name: str = Form(...),
        model_description: str = Form(...),
        model_overview: str = Form(...),
        frame: str = Form(...),
        image_id: int = Form(...),
        user_id: str = Form(...),
        pub: int = Form(...),
        hypara_path: str = Form(...),
        tag: str = Form(...),
        model_file: UploadFile = File(...),
):
    """FastAPI 处理模型创建"""
    model_data = {
        "model_name": model_name,
        "model_description": model_description,
        "model_overview_markdown": model_overview,
        "frame": frame,
        "image_id": image_id,
        "pub": pub,
        "user_id": user_id,
        "hypara_path": hypara_path,
        "tag": tag
    }

    # 调用添加模型服务
    result = await add_model_service(model_data, model_file)
    return result


@model_service.get('/public')
async def find_all_public_model():
    return ResultGenerator.gen_success_result(data=(await Model.find_all_public()))


@model_service.get('/waiting')
async def find_all_waiting_model():
    return ResultGenerator.gen_success_result(data=(await Model.find_all_waiting()))


@model_service.post('/waiting/{model_id}')
async def find_all_waiting_model(model_id):
    print("model_id", model_id)
    return ResultGenerator.gen_success_result(data=(await Model.set_waiting(model_id)))


@model_service.get('/getModelsByUserId/{user_id}')
async def get_models_by_user_id(user_id: str):
    models = await Model.get_models_by_user_id(user_id)
    return ResultGenerator.gen_success_result(data=models)


@model_service.get('/getModelsByTagName/{tag_name}')
async def get_models_id_by_tag(tag_name: str):
    models = await Model.get_models_by_tag_name(tag_name)
    return ResultGenerator.gen_success_result(data=models)
