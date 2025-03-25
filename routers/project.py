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
    project.storePath = upload_dir

    await project.save()

    return ResultGenerator.gen_success_result(message="创建项目成功")
