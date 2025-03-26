import json
import os
import shutil
import zipfile
from pathlib import Path

import docker
from fastapi import UploadFile

from models import Model, User
from utils.DockerFactory import DockerFactory
from utils.ResultGenerator import ResultGenerator

docker_factory = DockerFactory()


def unzip(zip_path: str, extract_to: str):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)


def delete_directory(directory_path: str):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)


async def add_model_service(model_dict: dict, model_file: UploadFile):
    global upload_path
    print(model_dict)
    if not model_dict.get("user_id"):
        return ResultGenerator.gen_fail_result(message="添加模型失败，未指定所属用户")

    if model_dict['user_id'] != '0' and (await User.filter(user_id=model_dict['user_id']).first() is None):
        print("添加模型失败：用户不存在")
        return ResultGenerator.gen_fail_result(message="用户不存在")

    model = await Model.add_model(model_dict)
    model_id = model.id
    if model_id is None:
        return ResultGenerator.gen_fail_result(message="添加模型失败，无法获取新的 model id")
    model_dict['model_id'] = model_id

    if not model_file:
        await Model.delete_model(model_id)
        return ResultGenerator.gen_fail_result(message="未上传模型文件")

    file_name = model_file.filename

    # 检查文件是不是压缩包格式
    if not file_name.endswith(".zip"):
        await Model.delete_model(model_id)
        return ResultGenerator.gen_fail_result(message="上传的文件必须是 .zip 压缩包")

    try:
        project_root = os.getcwd()  # 获取当前工作目录
        upload_dir = os.path.join(project_root, "data", "Model", str(model_id))
        upload_path = Path(upload_dir).resolve()

        # 保证要找的目录存在
        upload_path.mkdir(parents=True, exist_ok=True)

        # 保存 zip 文件
        zip_file_path = upload_path / model_file.filename
        with open(zip_file_path, "wb") as buffer:
            shutil.copyfileobj(model_file.file, buffer)
        # 解压文件
        unzip(str(zip_file_path), str(upload_path))
        # 删除 zip 文件
        os.remove(zip_file_path)

        await model.update_model_path(str(upload_path))

        # 检查有没有 Dockerfile
        dockerfile_path = upload_path / model_file.filename[:-4] / "Dockerfile"
        dockerfile_dir = upload_path / model_file.filename[:-4]

        if not dockerfile_path.exists():
            await Model.delete_model(model_id)
            delete_directory(str(upload_path))
            return ResultGenerator.gen_fail_result(message="Dockerfile not found")

        print(docker_factory.docker_client_pool)
        docker_core = docker_factory.docker_client_pool.get("tcp://localhost:2375")
        if not docker_core:
            await Model.delete_model(model_id)
            delete_directory(str(upload_path))
            return ResultGenerator.gen_fail_result(message="未找到对应主机的 DockerCore 实例")

        # 使用 Docker 客户端构建镜像
        try:
            # 假设 create_docker_image 是一个同步操作
            print('start build')
            result = docker_core.image_creator(str(model_id), str(dockerfile_dir))
            if not result:
                return ResultGenerator.gen_fail_result(message="创建镜像失败")
        except Exception as e:
            await Model.delete_model(model_id)
            delete_directory(str(upload_path))
            return ResultGenerator.gen_fail_result(message=f"创建镜像失败{e}")
    except Exception as e:
        await Model.delete_model(model_id)
        if os.path.exists(str(upload_path)):
            delete_directory(str(upload_path))
        return ResultGenerator.gen_fail_result(message=f"File upload or processing failed: {str(e)}")

    await Model.add_tag_to_model(model_dict['model_id'], model_dict['tag'])
    return ResultGenerator.gen_success_result(message='模型上传成功')


async def get_hypara_by_model_service(model_id: int):
    path = await Model.get_hypara_path_by_model_id(model_id)
    if not os.path.exists(path):
        return ResultGenerator.gen_fail_result(message='路径不存在')

    result = {}
    try:
        with open(path, 'r', encoding='utf-8') as file:
            result = json.load(file)
    except Exception as e:
        return ResultGenerator.gen_fail_result(message=f'读取文件失败{e}')

    return result
