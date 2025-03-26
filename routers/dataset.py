import os
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, Form, File
from pydantic import BaseModel

import models
from utils.ResultGenerator import ResultGenerator

dataset = APIRouter()


class Dataset(BaseModel):
    project_id: int
    dataset_name: str
    data_type: str
    data_size: float
    label: Optional[str] = None
    user_id: str
    introduction: Optional[str] = None
    data_url: str


@dataset.put('/')
async def add_dataset(dataset: Dataset):
    try:
        dataset_dict = dataset.dict()
        print(dataset_dict)
        success = await models.Dataset.add_dataset(dataset_dict)
        print("moca", success)

        if success:
            return ResultGenerator.gen_success_result(message="数据集添加成功")
        else:
            return ResultGenerator.gen_fail_result(message="数据集添加失败")
    except Exception as e:
        return ResultGenerator.gen_success_result(message=f"数据集添加失败{e}")


@dataset.put("/uploadFile")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    try:
        # 校验 UserID
        if not user_id:
            return ResultGenerator.gen_fail_result(message="UserID 不能为空")

        # 获取当前数据库中最大的 DatasetId
        dataset_id = await models.Dataset.find_max_dataset_id()
        if not dataset_id:
            return ResultGenerator.gen_fail_result(message="数据库中没有可用的数据集记录")

        # 构建目标路径（使用 DatasetId）
        project_root = os.getcwd()
        upload_dir = Path(os.path.join(project_root, "data", "dataset", str(dataset_id)))
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 获取文件名
        original_filename = file.filename
        if not original_filename:
            return ResultGenerator.gen_fail_result(message="文件名无效")

        # 校验文件格式是否为 ZIP
        if not original_filename.endswith(".zip"):
            return ResultGenerator.gen_fail_result(message="只支持 ZIP 格式的文件上传")

        # 构造保存的目标 ZIP 文件（使用原文件名）
        zip_file_path = upload_dir / original_filename
        with open(zip_file_path, "wb") as f:
            f.write(await file.read())

        # 解压 ZIP 文件
        unzip_file(zip_file_path, upload_dir)

        # 删除 ZIP 文件
        if zip_file_path.exists():
            zip_file_path.unlink()

        # 更新 DataUrl 字段到数据库
        data_url = str(upload_dir)
        is_updated = await models.Dataset.update_dataset_url(dataset_id, data_url)
        if not is_updated:
            return ResultGenerator.gen_fail_result(message="数据库更新失败，文件路径未能保存")

        # 返回成功结果
        return ResultGenerator.gen_success_result(message="文件上传并解压成功")
    except Exception as e:
        return ResultGenerator.gen_error_result(message="文件上传失败：{e}", code=500)


def unzip_file(zip_file_path: Path, target_dir: Path):
    # 解压 ZIP 文件到指定目录
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(target_dir)


@dataset.get('/public')
async def get_public_datasets():
    datasets = await models.Dataset.find_public_datasets()
    return ResultGenerator.gen_success_result(data=datasets)


@dataset.get('/')
async def getAllDatasets():
    datasets = await models.Dataset.find_all()
    if not list:
        return ResultGenerator.gen_fail_result(message="没有找到任何数据集")
    return ResultGenerator.gen_success_result(data=datasets)


@dataset.get('/{dataset_id}')
async def get_dataset_by_id(dataset_id: str):
    dataset = await models.Dataset.get(dataset_id=dataset_id)
    return ResultGenerator.gen_success_result(data=dataset)


@dataset.get('/findByUserId/{user_id}')
async def get_dataset_by_user(user_id: str):
    datasets = await models.Dataset.find_by_user_id(user_id)
    if not list:
        return ResultGenerator.gen_fail_result(message="没有找到任何数据集")
    return ResultGenerator.gen_success_result(data=datasets)
