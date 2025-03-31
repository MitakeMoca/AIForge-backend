import shutil
from pathlib import Path

from fastapi import HTTPException
from tortoise import fields
from datetime import datetime
from typing import List, Dict, Any
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
        model = await Model.get(model_id=project.model_id)

        # 创建模型
        model_file = model.model_path
        hypara_directory = "/root/data/Hypara/model/"
        store_path = hypara_directory + Project.generate_unique_filename("json")

        # 复制模型超参数文件
        new_hypara_path = hypara_directory + store_path
        try:
            # 模拟复制操作
            pass
        except Exception as e:
            return {"error": f"模型超参数文件复制失败: {str(e)}"}

        # 创建新的模型
        new_model = Model(
            model_name=project.project_name,
            model_description=project.description,
            model_path=model_file,
            hypara_path=new_hypara_path
        )
        await new_model.save()
        return {"message": "项目转模型成功"}

    @staticmethod
    def generate_unique_filename(extension: str):
        # 生成唯一的文件名
        import uuid
        return f"hypara_{uuid.uuid4()}_{int(datetime.now().timestamp())}.{extension}"

    @staticmethod
    async def copy_directory(source: Path, target: Path):
        """Recursively copy a directory and its contents."""
        # Check if the target directory exists, create if not
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)

        # Iterate through the directory and copy files
        for entry in source.iterdir():
            target_path = target / entry.name
            if entry.is_dir():
                await Project.copy_directory(entry, target_path)  # Recurse for directories
            else:
                shutil.copy(entry, target_path)  # Copy files

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

