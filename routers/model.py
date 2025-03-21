from fastapi import APIRouter, Form, UploadFile, File
from pydantic import BaseModel

from services.model import add_model_service

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
