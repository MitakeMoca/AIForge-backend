from fastapi import APIRouter

from models import Tag
from utils.ResultGenerator import ResultGenerator

tag = APIRouter()


@tag.get('/name')
async def get_all_tags():
    # 获取所有标签
    tags_name = await Tag.get_all_tags_name()  # 提取 tagName 列表
    return ResultGenerator.gen_success_result(data=tags_name)
