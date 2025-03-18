import docker
import os
import threading
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from time import sleep


class DockerCore:
    def __init__(self, docker_host: str = "unix:///var/run/docker.sock"):
        # 初始化 Docker 客户端
        self.client = docker.DockerClient(base_url=docker_host)

        # 初始化容器名称到ID的映射
        self.container_name_to_id = {}
        self.gpu_max = 0
        self.gpu_used = 0
        self.cpu_max = 0
        self.cpu_used = 0

        # 初始化容器信息
        self.initialize_container_map()

    def initialize_container_map(self):
        # 获取所有容器并存储容器名称到ID的映射
        containers = self.client.containers.list(all=True)
        for container in containers:
            name = container.name
            container_id = container.id
            self.container_name_to_id[name] = container_id

    def create_container(self, image_name: str, project_id: int, gpu_needed: Optional[int], cpu_needed: Optional[int],
                         port: int, model_path: str, project_store_path: str, train_dataset_store_path: str,
                         test_dataset_store_path: str, project_dao: Any) -> List[str]:
        warnings = []

        container_name = f"project_{project_id}"
        if gpu_needed and (gpu_needed + self.gpu_used > self.gpu_max):
            warnings.append("GPU resources insufficient")
        if cpu_needed and (cpu_needed + self.cpu_used > self.cpu_max):
            warnings.append("CPU resources insufficient")
        if not self._image_exists(image_name):
            warnings.append("Image does not exist")
        if container_name in self.container_name_to_id:
            warnings.append(f"Container {container_name} already exists")
            warnings.append("403")
            return warnings

        if not warnings:
            volumes = {
                "/app/model": {"bind": model_path, "mode": "rw"},
                "/app/Project": {"bind": project_store_path, "mode": "rw"},
                "/app/Train_Dataset": {"bind": train_dataset_store_path, "mode": "rw"},
                "/app/Test_Dataset": {"bind": test_dataset_store_path, "mode": "rw"}
            }
            try:
                # 创建并启动容器
                container = self.client.containers.create(
                    image=image_name,
                    name=container_name,
                    ports={f"80/tcp": port},
                    volumes=volumes
                )
                container.start()

                # 更新容器ID映射
                self.container_name_to_id[container_name] = container.id

                # 更新项目状态
                project_dao.update_project_status_by_id(project_id, "wait")

                # 更新资源使用情况
                self.gpu_used += gpu_needed or 0
                self.cpu_used += cpu_needed or 0

                warnings.append(f"Success! Container ID is {container.id}")
                warnings.append("200")
            except Exception as e:
                warnings.append(str(e))
                warnings.append("500")
        return warnings

    def _image_exists(self, image_name: str) -> bool:
        try:
            self.client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def check_container_status(self, container_name: str) -> str:
        if container_name not in self.container_name_to_id:
            raise HTTPException(status_code=404, detail=f"Container {container_name} does not exist")

        container = self.client.containers.get(self.container_name_to_id[container_name])
        return container.status

    def container_log(self, container_name: str):
        if container_name not in self.container_name_to_id:
            raise HTTPException(status_code=404, detail=f"Container {container_name} does not exist")

        container = self.client.containers.get(self.container_name_to_id[container_name])
        logs = container.logs(stream=True)
        for log in logs:
            print(log.decode("utf-8"))

    def exec_container_log(self, project_id: int, command: str, project_dao: Any) -> List[str]:
        warnings = []
        container_name = f"project_{project_id}"
        try:
            container = self.client.containers.get(self.container_name_to_id[container_name])
            exec_log = container.exec_run(command)
            logs = exec_log.output.decode("utf-8")
            print(logs)

            # Update project status
            project_dao.update_project_status_by_id(project_id, "running")

            warnings.append("200")
        except Exception as e:
            warnings.append(str(e))
            project_dao.update_project_status_by_id(project_id, "stopped")
            warnings.append("500")
        return warnings

    def stop_container(self, project_id: int, project_dao: Any):
        container_name = f"project_{project_id}"
        try:
            container = self.client.containers.get(self.container_name_to_id[container_name])
            container.stop()
            container.remove()

            # Update project status
            project_dao.update_project_status_by_id(project_id, "stopped")

            self.container_name_to_id.pop(container_name, None)
        except Exception as e:
            print(f"Error stopping container: {e}")

    def list_images(self) -> List[str]:
        images = self.client.images.list()
        return [image.tags[0] if image.tags else "untagged" for image in images]

