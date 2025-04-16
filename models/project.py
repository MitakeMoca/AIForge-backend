import os
import shutil
from pathlib import Path

from fastapi import HTTPException
from tortoise import fields
from datetime import datetime
from typing import List, Dict, Any

from services.model import add_model_without_file
from utils.DockerCore import DockerCore
from models.basemodel import BaseModel  # 基类，假设BaseModel已经定义好
from models.model import Model  # 假设Model模型已经定义
from models.dataset import Dataset  # 假设Dataset模型已经定义
from utils.DockerFactory import DockerFactory
from utils.ResultGenerator import ResultGenerator


class Project(BaseModel):
    project_id = fields.IntField(pk=True)
    project_name = fields.CharField(max_length=255)
    description = fields.TextField()
    user_id = fields.CharField(max_length=255)
    status = fields.CharField(max_length=100, default="init")
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)
    visibility = fields.CharField(max_length=100)
    model_id = fields.IntField()
    train_dataset_id = fields.IntField()
    test_dataset_id = fields.IntField()
    store_path = fields.CharField(max_length=255, default="")
    project_type = fields.CharField(max_length=100)

    class Meta:
        table = "project"

    @staticmethod
    async def add_project(project: dict):
        project['create_time'] = datetime.now()
        project['update_time'] = datetime.now()
        project = await Project.create(**project)
        return project

    @staticmethod
    async def find_all():
        # 获取所有项目的列表
        projects = await Project.all()  # 获取所有项目
        return projects

    @staticmethod
    async def find_by_id(project_id: int):
        project = await Project.get(project_id=project_id)
        return project

    @staticmethod
    async def find_by_user_id(user_id: str):
        projects = await Project.filter(user_id=user_id)
        return projects

    @staticmethod
    async def update_model_id_by_id(project_id: int, model_id: int):
        project = await Project.get(project_id=project_id)
        project.model_id = model_id
        await project.save()

        # 将模型的文件拷贝到项目目录
        model = await Model.get(id=model_id)
        model_file = model.model_path
        project_root = os.getcwd()
        project_file = os.path.join(project_root, "data", "Project", str(project_id))
        # 清空现有项目的目录
        if os.path.exists(project_file):
            shutil.rmtree(project_file)
        # 复制模型文件到项目目录
        try:
            shutil.copytree(model_file, project_file)
        except IOError as e:
            print(f"Error copying model files: {e}")

        return {"detail": "Model ID updated"}

    @staticmethod
    async def update_train_dataset_id_by_id(project_id: int, train_dataset_id: int):
        project = await Project.get(project_id=project_id)
        project.train_dataset_id = train_dataset_id
        await project.save()
        return {"detail": "Train dataset ID updated"}

    @staticmethod
    async def update_test_dataset_id_by_id(project_id: int, test_dataset_id: int):
        project = await Project.get(project_id=project_id)
        project.test_dataset_id = test_dataset_id
        await project.save()
        return {"detail": "Test dataset ID updated"}

    @staticmethod
    async def update_description_by_id(project_id: int, description: str):
        project = await Project.get(project_id=project_id)
        project.description = description
        await project.save()
        return {"detail": "Description updated"}

    @staticmethod
    async def update_project_name_by_id(project_id: int, project_name: str):
        project = await Project.get(project_id=project_id)
        project.project_name = project_name
        await project.save()
        return {"detail": "Project name updated"}

    @staticmethod
    async def update_visibility_by_id(project_id: int, visibility: str):
        project = await Project.get(project_id=project_id)
        project.visibility = visibility
        await project.save()
        return {"detail": "Visibility updated"}

    @staticmethod
    async def update_project_status_by_id(project_id: int, status: str):
        project = await Project.get(project_id=project_id)
        project.status = status
        await project.save()
        return {"detail": "Project status updated"}

    @staticmethod
    async def update_project_type_by_id(project_id: int, project_type: str):
        project = await Project.get(project_id=project_id)
        project.project_type = project_type
        await project.save()
        return {"detail": "Project type updated"}

    @staticmethod
    async def delete_by_id(project_id: int):
        project = await Project.get(project_id=project_id)
        await project.delete()
        return {"detail": "Project deleted"}

    @staticmethod
    async def create_project(project_id: int):
        project = await Project.get(project_id=project_id)

        # 查找模型
        model = await Model.get(model_id=project.model_id)

        # 查找数据集
        train_dataset = await Dataset.get(dataset_id=project.train_dataset_id)
        test_dataset = await Dataset.get(dataset_id=project.test_dataset_id)

        docker_core = DockerCore()  # DockerCore 用于容器操作
        container_id = docker_core.container_create(
            model.model_id,
            project.project_id,
            project.store_path,
            train_dataset.data_url,
            test_dataset.data_url
        )

        return {"container_id": container_id}

    @staticmethod
    async def run_project(project_id: int, command: str, hypara: Dict[str, Any]):
        project = await Project.find_by_id(project_id)
        if project:
            docker = DockerFactory.docker_client_pool['tcp://localhost:2375']
            complete_command = "python -u /app/model/Code/" + command + " "
            for key, value in hypara.items():
                complete_command += "--" + key + " " + value + " "
            try:
                return await docker.exec_container_log(project_id, complete_command, project)
            except Exception as e:
                print(f"exec_container_log error: {e}")
                return ResultGenerator.gen_error_result(code=500, message=f"项目运行失败{e}")
        else:
            return ResultGenerator.gen_error_result(code=404, message="项目不存在")

    @staticmethod
    async def stop_project(project_id: int):
        project = await Project.get(project_id=project_id)

        docker_core = DockerCore()
        docker_core.container_stop(project.store_path)  # 使用项目的store_path来停止容器
        return {"status": "Container stopped"}

    @staticmethod
    async def project_to_model(project: 'Project'):
        # 查找模型
        model = await Model.get(id=project.model_id)

        # 创建模型
        model_file = model.model_path
        project_root = os.getcwd()
        hypara_directory = os.path.join(project_root, 'data', 'Hypara', 'model')  # 连接相对路径
        new_hypara = hypara_directory + Project.generate_unique_filename("json")
        model_hypara = model.hypara_path

        Path(hypara_directory).mkdir(parents=True, exist_ok=True)  # 创建目录
        # 复制模型超参数文件
        try:
            shutil.copy(model_hypara, new_hypara)
        except IOError as e:
            return ResultGenerator.gen_fail_result(message=f"复制超参数文件失败: {str(e)}")

        # 创建新的模型
        model = await Model.add_model({
            "model_name": project.project_name,
            "model_description": project.description,
            "model_overview_markdown": model.model_overview_markdown,
            "frame": model.frame,
            "image_id": model.image_id,
            "user_id": project.user_id,
            "pub": 0,
            "hypara_path": new_hypara,
            "model_date": datetime.now(),
            "tag": model.tag,
        })

        model = await add_model_without_file(model)
        print(model)
        new_model_path = model.model_path
        try:
            # 复制模型文件
            shutil.copytree(model_file, new_model_path)
            project_file = project.store_path
            # 复制项目文件
            if os.path.exists(project_file):
                shutil.rmtree(project_file)
            shutil.copytree(new_model_path, project_file)  # 复制模型文件到项目目录
        except IOError as e:
            return ResultGenerator.gen_fail_result(message=f"复制模型文件失败: {str(e)}")

        return ResultGenerator.gen_success_result(message="模型创建成功", data=model)

    @staticmethod
    def generate_unique_filename(extension: str):
        # 生成唯一的文件名
        import uuid
        return f"hypara_{uuid.uuid4()}_{int(datetime.now().timestamp())}.{extension}"


    @staticmethod
    async def predict(project_id: int, command: str, hypara: Dict[str, str]):
        try:
            project = await Project.get(project_id=project_id)

            model = await Model.get(model_id=project.model_id)

            docker_core = DockerCore()

            complete_command = f"python -u /app/model/Code/{command} "
            for key, value in hypara.items():
                complete_command += f"--{key} {value} "

            complete_command += f"--model {model.model_path}"

            result = docker_core.run_command(project.store_path, complete_command)

            return {"result": result}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

