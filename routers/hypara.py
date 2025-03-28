import json
import os
import uuid
from typing import Dict

from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel

from models import Hypara
from utils.ResultGenerator import ResultGenerator
from services.model import get_hypara_by_model_service

hypara = APIRouter()


class Hyperparameters(BaseModel):
    # 定义请求体字段，假设字段是任意的，具体结构根据实际情况调整
    hyperparameters: dict


def generate_unique_file_name(extension: str) -> str:
    unique_identifier = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp() * 1000)  # 当前时间的毫秒表示
    return f"hypara_{unique_identifier}_{timestamp}.{extension}"


@hypara.put("/")
async def create_hypara_field(hyperparameters: Hyperparameters):
    # 目录
    project_root = os.getcwd()  # 获取当前工作目录
    print("hyperparameters", hyperparameters)
    hypara_directory = os.path.join(project_root, "data", "Hypara", "model")  # 连接相对路径

    # 生成唯一的文件名
    store_path = os.path.join(hypara_directory, generate_unique_file_name("json"))

    # 创建目录
    if not os.path.exists(hypara_directory):
        os.makedirs(hypara_directory)

    # 保存超参数到 JSON 文件
    try:
        with open(store_path, "w", encoding="utf-8") as file:
            # 将超参数写入文件，确保中文不被转义
            json.dump(hyperparameters.hyperparameters, file, ensure_ascii=False, indent=4)
    except IOError as e:
        return ResultGenerator.gen_fail_result(message=f"保存文件失败: {str(e)}")

    # 输出并返回存储路径的绝对路径
    absolute_store_path = os.path.abspath(store_path)
    print(f"File has been saved to: {absolute_store_path}")

    # 返回存储路径
    return ResultGenerator.gen_success_result(data={"storePath": store_path})


@hypara.get("/path/{store_path}")
async def get_hypara_field_by_path(store_path: str):
    hypara_fields = {}

    # 读取 JSON 文件
    try:
        if not os.path.exists(store_path):
            return ResultGenerator.gen_error_result(code=400, message="文件路径不存在")

        with open(store_path, "r", encoding="utf-8") as json_file:
            fields = json.load(json_file)

        # 将字段列表放入 hyparaFields 中
        hypara_fields = fields
    except Exception as e:
        return ResultGenerator.gen_error_result(code=500, message=f"获取超参数文件失败: {str(e)}")

    return hypara_fields


@hypara.get("/project/{project_id}")
async def get_hypara_by_project_id(project_id: int):
    hypara_paths = await Hypara.find_by_project_id(project_id)

    all_hypara_fields = {}

    # 遍历所有路径，获取超参数字段
    for path in hypara_paths:
        hypara_fields = await get_hypara_field_by_path(path)
        all_hypara_fields.update(hypara_fields)
    print(all_hypara_fields)
    return ResultGenerator.gen_success_result(data=all_hypara_fields)


@hypara.get('/getHyparaByProjectId/{project_id}')
async def get_hypara_by_project(project_id: int):
    hyparas = await Hypara.find_by_project_id(project_id)
    return ResultGenerator.gen_success_result(data=hyparas)


@hypara.get('/getHyparaPathByModelId/{model_id}')
async def get_hypara_by_model(model_id: int):
    hyparas = await get_hypara_by_model_service(model_id)
    return ResultGenerator.gen_success_result(data=hyparas)


class HyparaParams(BaseModel):
    params: dict


@hypara.post('/add/{project_id}')
async def add_hypara(project_id: int, params: HyparaParams):
    params = params.params
    store_path = os.getcwd()
    store_dir = os.path.join(store_path, "data", "Hypara", "project")
    store_path = str(store_dir) + f'/{project_id}.json'
    if not os.path.exists(store_dir):
        os.makedirs(store_dir)
    if os.path.exists(store_path):
        os.remove(store_path)

    try:
        with open(store_path, 'w', encoding='utf-8') as file:
            json.dump(params, file, ensure_ascii=False, indent=4)
    except Exception as e:
        return ResultGenerator.gen_error_result(code=500, message=f"保存文件失败: {e}")

    hypara = await Hypara.create(hypara_id=str(uuid.uuid4()), project_id=project_id, store_path=store_path)
    return ResultGenerator.gen_success_result(message="超参数添加成功")