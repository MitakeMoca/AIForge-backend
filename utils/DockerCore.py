from typing import Optional

import docker
import os

from utils.ImageList import ImageList
from utils.ResultGenerator import ResultGenerator


class DockerCore:
    def __init__(self, docker_host):
        self.docker_client = docker.DockerClient(base_url=docker_host, timeout=None)
        self.container_name_to_id = {}  # 映射容器名称到容器 ID
        self.cpu_max = 0
        self.cpu_use = 0  # CPU
        self.gpu_max = 0
        self.gpu_use = 0

        # 初始化容器名称到ID的映射
        self.initialize_container_map()

    def initialize_container_map(self):
        """列出所有容器并初始化名称到ID的映射"""
        containers = self.docker_client.containers.list(all=True)
        for container in containers:
            name = container.name
            container_id = container.id
            if name:
                self.container_name_to_id[name] = container_id
                print(f"name: {name}, id: {container_id}")

    async def container_creator(self, image_name: str, project_id: int, gpu_need: Optional[int], cpu_need: Optional[int],
                                port: int, model_path: str, project_store_path: str, train_dataset_store_path: str,
                                test_dataset_store_path: str, project_dao_impl):

        warnings = []
        container_name = f"project_{project_id}"

        if gpu_need and gpu_need + self.gpu_use > self.gpu_max:
            return ResultGenerator.gen_fail_result("GPU 资源不足，无法分配")
        if cpu_need and cpu_need + self.cpu_use > self.cpu_max:
            return ResultGenerator.gen_fail_result("CPU 资源不足，无法分配")

        # 镜像检查
        if not ImageList.search_image(image_name + ":latest"):
            return ResultGenerator.gen_fail_result("镜像不存在")

        # 容器是否已存在检查
        if container_name in self.container_name_to_id:
            return ResultGenerator.gen_error_result(code=403, message=f"容器 {container_name} 已存在")

        try:
            # 创建容器
            container = self.docker_client.containers.create(
                image=f"{image_name}:latest",
                name=container_name,
                ports={80: port},
                volumes={
                    "/app/model": {"bind": model_path, "mode": "rw"},
                    "/app/Project": {"bind": project_store_path, "mode": "rw"},
                    "/app/Train_Dataset": {"bind": train_dataset_store_path, "mode": "rw"},
                    "/app/Test_Dataset": {"bind": test_dataset_store_path, "mode": "rw"}
                }
            )
            container.start()

            # 更新状态
            await project_dao_impl.update_project_status_by_id(project_id, "wait")

            # 更新资源使用情况
            self.gpu_use += gpu_need if gpu_need else 0
            self.cpu_use += cpu_need if cpu_need else 0

            self.container_name_to_id[container_name] = container.id

            return ResultGenerator.gen_success_result(f"Success! Container Id 为 {container.id}")

        except Exception as e:
            return ResultGenerator.gen_error_result(code=500, message=f"容器创建失败: {str(e)}")


    def image_creator(self, image_name, pathname):
        """创建镜像并返回状态"""
        if self.search_image(image_name):
            return ResultGenerator.gen_fail_result(message="镜像已存在")
        else:
            try:
                dockerfile_dir = os.path.abspath(pathname)

                self._build_image(dockerfile_dir, image_name)

                return ResultGenerator.gen_success_result(message="镜像创建成功")  # 返回成功状态
            except Exception as e:
                print(f"镜像创建失败: {e}")
                return ResultGenerator.gen_success_result(message=f"镜像创建失败{e}")

    def _build_image(self, dockerfile_dir, image_name):
        """构建镜像的具体过程"""
        try:
            print(dockerfile_dir, image_name)
            for line in self.docker_client.images.build(path=dockerfile_dir, tag=image_name):
                print(line)
            print(f"镜像构建成功: {image_name}")
            ImageList.add_image(image_name)
        except Exception as e:
            print(f"构建镜像失败: {e}")

    def search_image(self, image_name):
        """搜索镜像是否存在"""
        images = self.docker_client.images.list()
        for image in images:
            if image_name in image.tags:
                return True
        return False

    def check_container_status(self, container_name):
        """检查容器状态"""
        if container_name not in self.container_name_to_id:
            return f"容器 {container_name} 不存在"
        container_info = self.docker_client.containers.get(self.container_name_to_id[container_name]).attrs
        status = container_info['State']['Status']
        return status

    def container_log(self, container_name):
        """获取容器日志"""
        try:
            container = self.docker_client.containers.get(self.container_name_to_id[container_name])
            logs = container.logs(stream=True)
            for log in logs:
                print(log.decode("utf-8"))
        except docker.errors.DockerException as e:
            print(f"获取日志失败: {e}")

    def exec_container_log(self, project_id, command, project_dao_impl):
        """执行容器内的命令并获取日志"""
        container_name = f"project_{project_id}"
        try:
            container = self.docker_client.containers.get(self.container_name_to_id[container_name])
            result = container.exec_run(command, tty=False, stream=True)
            for log in result:
                print(log.decode("utf-8"))
            project_dao_impl.update_project_status_by_id(project_id, "finished")
        except docker.errors.DockerException as e:
            project_dao_impl.update_project_status_by_id(project_id, "stopped")
            print(f"执行命令失败: {e}")

    def stop_container(self, project_id, project_dao_impl):
        """停止并删除容器"""
        container_name = f"project_{project_id}"
        try:
            container = self.docker_client.containers.get(self.container_name_to_id[container_name])
            container.stop()
            container.remove()
            self.container_name_to_id.pop(container_name, None)
            project_dao_impl.update_project_status_by_id(project_id, "stopped")
        except docker.errors.DockerException as e:
            print(f"停止容器失败: {e}")

    def list_images(self):
        """列出所有镜像"""
        images = self.docker_client.images.list()
        result = []
        for image in images:
            if image.tags:
                result.append(image.tags[0])
            else:
                result.append("untagged")
        return result
