import os

from fastapi import APIRouter
from pydantic import BaseModel

from models import Project
from utils.ResultGenerator import ResultGenerator

project = APIRouter()


class ProjectCreateRequest(BaseModel):
    ProjectName: str
    Description: str
    UserId: str
    CreateTime: str
    modelId: int
    Test_DatasetId: int
    Train_DatasetId: int
    ProjectType: str

    class Config:
        orm_mode = True


@project.get('/findByUserId/{user_id}')
async def find_project_by_user(user_id: str):
    projects = await Project.find_by_user_id(user_id)
    return ResultGenerator.gen_success_result(data=projects)


@project.put('/')
async def add_project(request: ProjectCreateRequest):
    project_dict = {
        'project_name': request.ProjectName,
        'description': request.Description,
        'user_id': request.UserId,
        'model_id': request.modelId,
        'test_dataset_id': request.Test_DatasetId,
        'train_dataset_id': request.Train_DatasetId,
        'visibility': "0",
        'project_type': request.ProjectType
    }
    project = await Project.add_project(project_dict)
    project_root = os.getcwd()
    upload_dir = os.path.join(project_root, "data", "Project", f"{project.project_id}")
    await Project.filter(project_id=project.project_id).update(store_path=upload_dir)
    project = await Project.get(project_id=project.project_id)
    return ResultGenerator.gen_success_result(message="创建项目成功", data=project)


@project.get('/{project_id}')
async def get_project(project_id: str):
    project = await Project.get(project_id=project_id)
    return ResultGenerator.gen_success_result(data=project)


@project.post('/projectType/{project_id}/{project_type}')
async def update_project_type(project_id: int, project_type: str):
    await Project.update_project_type_by_id(project_id, project_type)
    return ResultGenerator.gen_success_result(message="修改项目类型成功")


@project.post('/model/{project_id}/{model_id}')
async def update_project_model(project_id: int, model_id: int):
    await Project.update_model_id_by_id(project_id, model_id)
    return ResultGenerator.gen_success_result(message="设置项目模型成功")


@project.post('/train_dataset/{project_id}/{dataset_id}')
async def update_train_dataset(project_id: int, dataset_id: int):
    await Project.update_train_dataset_id_by_id(project_id, dataset_id)
    return ResultGenerator.gen_success_result(message="设置项目训练集成功")


@project.post('/test_dataset/{project_id}/{dataset_id}')
async def update_test_dataset(project_id: int, dataset_id: int):
    await Project.update_test_dataset_id_by_id(project_id, dataset_id)
    return ResultGenerator.gen_success_result(message="设置项目测试集成功")
