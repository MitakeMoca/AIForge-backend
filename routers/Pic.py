import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile
from starlette.responses import StreamingResponse, FileResponse

from models import User
from utils.ResultGenerator import ResultGenerator

pic = APIRouter()


@pic.post('/')
async def upload_file(file: UploadFile):
    if not file:
        return ResultGenerator.gen_fail_result(message="没有选择文件")

    upload_dir = os.getcwd()
    name = f"{uuid4().hex}.png"
    file_path = os.path.join(upload_dir, "data", "pic", name)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return ResultGenerator.gen_success_result(data={"file_path": f"/static/{name}"})


@pic.get("/path/{file_path}")
async def download_by_path(file_path: str):
    file_path = Path(file_path).resolve()

    # 返回文件作为 Blob
    return FileResponse(file_path, media_type="application/octet-stream", filename=file_path.name)


@pic.get("/{user_id}")
async def product_download(user_id: str):
    user = await User.find_by_id(user_id)
    if not user or not user.image_id:
        return ResultGenerator.gen_fail_result(message="没有找到该用户的图片")

    file_path = user.image_id
    if not Path(file_path).exists():
        return ResultGenerator.gen_fail_result(message="文件不存在")

    return ResultGenerator.gen_success_result(data=StreamingResponse(open(file_path, "rb"), media_type="application/octet-stream"))
