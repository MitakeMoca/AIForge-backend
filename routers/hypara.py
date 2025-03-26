import json
import os
import uuid

from fastapi import APIRouter, HTTPException
from datetime import datetime
from pydantic import BaseModel

from models import Hypara
from utils.ResultGenerator import ResultGenerator

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


@hypara.get('/getHyparaByProjectId/{project_id}')
async def get_hypara_by_project(project_id: int):
    hyparas = await Hypara.find_by_project_id(project_id)
    return ResultGenerator.gen_success_result(data=hyparas)