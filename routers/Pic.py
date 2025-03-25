from pathlib import Path

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from models import User
from utils.ResultGenerator import ResultGenerator

pic = APIRouter()


@pic.get("/{user_id}")
async def product_download(user_id: str):
    user = await User.find_by_id(user_id)
    if not user or not user.image_id:
        return ResultGenerator.gen_fail_result(message="没有找到该用户的图片")

    file_path = user.image_id
    if not Path(file_path).exists():
        return ResultGenerator.gen_fail_result(message="文件不存在")

    return ResultGenerator.gen_success_result(data=StreamingResponse(open(file_path, "rb"), media_type="application/octet-stream"))
