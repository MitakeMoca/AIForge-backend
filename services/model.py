from fastapi import UploadFile

from models import Model, User
from utils.ResultGenerator import ResultGenerator


async def add_model_service(model_dict: dict, model_file: UploadFile):
    print(model_dict)
    if not model_dict.get("user_id"):
        return ResultGenerator.gen_fail_result(message="添加模型失败，未指定所属用户")

    if model_dict['user_id'] != '0' and (await User.filter(user_id=model_dict['user_id']).first() is None):
        print("添加模型失败：用户不存在")
        return ResultGenerator.gen_fail_result(message="用户不存在")

    model_id = (await Model.add_model(model_dict)).id
    if model_id is None:
        return ResultGenerator.gen_fail_result(message="添加模型失败，无法获取新的 model id")
    model_dict['model_id'] = model_id
