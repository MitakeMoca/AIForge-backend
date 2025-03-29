import os
from typing import Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel

from models import Project, Model
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


class TreeNode:
    def __init__(self, path: str, node_type: str, label: str, children: List['TreeNode'] = None):
        self.path = path
        self.type = node_type  # folder 或 file
        self.label = label
        self.children = children or []  # 如果没有提供子节点，默认为空列表

    def __repr__(self):
        return f"TreeNode(path={self.path}, type={self.type}, label={self.label}, children={self.children})"


@project.get('/findByUserId/{user_id}')
async def find_project_by_user(user_id: str):
    projects = await Project.find_by_user_id(user_id)
    return ResultGenerator.gen_success_result(data=projects)


def build_file_tree(directory_path: str, project_id: int) -> TreeNode:
    node = TreeNode(path=directory_path, node_type="folder", label=os.path.basename(directory_path))

    children = []
    try:
        files = os.listdir(directory_path)
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            relative_path = file_path.split(f"project/{project_id}/", 1)[-1]

            child_node = TreeNode(
                path=relative_path,
                node_type="folder" if os.path.isdir(file_path) else "file",
                label=file_name
            )

            if os.path.isdir(file_path):
                child_node.children = build_file_tree(file_path, project_id).children

            children.append(child_node)
    except PermissionError:
        pass

    node.children = children
    return node


@project.get("/tree/{project_id}")
async def get_tree(project_id: int):
    project_root = os.getcwd()
    path = os.path.join(project_root, "data", "Project", f"{project_id}")
    # 检查路径是否存在
    if not os.path.exists(path) or not os.path.isdir(path):
        return ResultGenerator.gen_error_result(code=400, message="路径不存在或不是一个目录")

    root_node = build_file_tree(path, project_id)

    return ResultGenerator.gen_success_result(data=root_node.children)


@project.put('/Docker/{project_id}')
async def create_project_docker(project_id: int):
    project = await Project.find_by_id(project_id)
    if not project:
        return ResultGenerator.gen_error_result(code=404, message="项目不存在")

    model = await Model.find_by_id(project.model_id)
    if not model:
        return ResultGenerator.gen_error_result(code=404, message="模型不存在")

    train_dataset = await find_dataset_by_id(project.train_dataset_id)
    if not train_dataset:
        return ["训练集不存在", "404"]

    test_dataset = await find_dataset_by_id(project.test_dataset_id)
    if not test_dataset:
        return ["测试集不存在", "404"]

    # 模拟调用 Docker 容器创建逻辑
    result = await container_creator(
        str(model.model_id),
        project.project_id,
        model.model_path,
        project.store_path,
        train_dataset.data_url,
        test_dataset.data_url
    )
    return result



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
    os.makedirs(upload_dir, exist_ok=True)
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
