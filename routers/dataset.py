from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

import models
from utils.ResultGenerator import ResultGenerator

dataset = APIRouter()


class Dataset(BaseModel):
    project_id: int
    data_set_name: str
    data_type: str
    data_size: float
    label: Optional[str] = None
    user_id: int
    introduction: Optional[str] = None
    data_url: str


@dataset.put('/')
async def add_dataset(dataset: Dataset):
    try:
        dataset_dict = dataset.dict()

        success = models.Dataset.add_dataset(dataset_dict)

        if success:
            return ResultGenerator.gen_success_result(message="数据集添加成功")
        else:
            return ResultGenerator.gen_fail_result(message="数据集添加失败")
    except Exception as e:
        return ResultGenerator.gen_success_result(message=f"数据集添加失败{e}")
