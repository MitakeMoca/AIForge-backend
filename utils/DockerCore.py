import asyncio
from typing import Optional

import docker
import os

from utils.ImageList import ImageList
from utils.ResultGenerator import ResultGenerator
from utils.WebSocketConfig import active_connections


class DockerCore:
    def __init__(self, docker_host):
        self.docker_client = docker.DockerClient(base_url=docker_host, timeout=None)
        self.container_name_to_id = {}  # 映射容器名称到容器 ID
        self.containers = {}    # 映射容器名到容器
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

    async def container_creator(self, image_name: str, project_id: int, gpu_need: Optional[int],
                                cpu_need: Optional[int],
                                port: int, model_path: str, project_store_path: str, train_dataset_store_path: str,
                                test_dataset_store_path: str, project_dao_impl):

        container_name = f"project_{project_id}"

        if gpu_need and gpu_need + self.gpu_use > self.gpu_max:
            return ResultGenerator.gen_fail_result("GPU 资源不足，无法分配")
        if cpu_need and cpu_need + self.cpu_use > self.cpu_max:
            return ResultGenerator.gen_fail_result("CPU 资源不足，无法分配")

        # 镜像检查
        image_name = image_name + ":latest"
        print(f"img_name:{image_name} {ImageList.image_list}")
        if not ImageList.search_image(image_name):
            return ResultGenerator.gen_fail_result("镜像不存在")

        # 容器是否已存在检查
        if container_name in self.container_name_to_id:
            return ResultGenerator.gen_error_result(code=403, message=f"容器 {container_name} 已存在")

        try:
            model_path = model_path.replace("\\", "/")
            print("构建镜像名:", image_name)
            print(truncate_path_from_data(model_path))
            # 创建容器
            container = self.docker_client.containers.create(
                image=image_name,
                name=container_name,
                tty=True,
                stdout=True,
                stderr=True,
                detach=True
            )
            # 先创建但是还不运行
            # container.start()

            # 更新状态
            await project_dao_impl.update_project_status_by_id(project_id, "wait")

            # 更新资源使用情况
            self.gpu_use += gpu_need if gpu_need else 0
            self.cpu_use += cpu_need if cpu_need else 0

            self.container_name_to_id[container_name] = container.id
            self.containers[container_name] = container

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

    async def exec_container_log(self, project_id, command, project_dao_impl):
        from models import Project
        container_name = f"project_{project_id}"
        container = self.containers[container_name]

        try:
            # 创建 exec 命令
            exec_id = self.docker_client.api.exec_create(
                container=container_id,
                cmd=command.split(),
                stdout=True,
                stderr=True,
                tty=False
            )["Id"]

            # 启动 exec 命令（注意：是同步生成器，所以要放到线程池里跑）
            def _start_exec():
                return self.docker_client.api.exec_start(exec_id, stream=True)

            stream = await loop.run_in_executor(None, _start_exec)

            # 读取输出（也放在 executor 中异步迭代）
            for frame in stream:
                message = frame.decode("utf-8").strip()
                result = {"message": message}

                # 模拟发送（这里只是打印）
                print(f"[{container_id}] {result}")

            # 成功结束，更新状态
            await Project.update_project_status_by_id(project_id, "finished")
            return ResultGenerator.gen_success_result(message='项目运行成功')
        except Exception as e:
            await self.stop_container(project_id, await Project.find_by_id(project_id))
            print(f"[ERROR] moca {e}")
            return ResultGenerator.gen_error_result(code=500, message=f"[ERROR] {e}")

    async def stop_container(self, project_id: int, project):
        from models import Project
        container_name = f"project_{project_id}"
        print(f"container_name: {project_id }")

        try:
            containers = self.docker_client.containers.list(all=True)

            # 输出所有容器的容器名称和容器 ID
            print("当前 Docker 中的所有容器：")
            for container in containers:
                print(f"Container Name: {container.name}, Container ID: {container.id}, Status: {container.status}")
            container = self.docker_client.containers.get(container_name)
            container.stop()
            container.remove()

            # 更新项目状态
            await Project.update_project_status_by_id(project_id, "stopped")

            # 移除容器名记录
            self.container_name_to_id.pop(container_name, None)

            return ResultGenerator.gen_success_result(message=f"暂停容器 {container_name} 成功")

        except Exception as e:
            print(f"[ERROR] 停止容器失败: {e}")
            return ResultGenerator.gen_error_result(code=500, message="停止容器时出错")

    def list_images(self):
        """列出所有镜像"""
        images = self.docker_client.images.list()
        result = []
        for image in images:
            print(image)
            if image.tags:
                for tag in image.tags:
                    result.append(tag)
            else:
                result.append("untagged")
        return result


def windows_path_to_docker(windows_path: str) -> str:
    # 替换盘符：D: -> d
    drive, path_after_drive = os.path.splitdrive(windows_path)
    drive_letter = drive[0].lower()
    # 替换 \ 或 / 为 Linux 风格的 /
    unix_style_path = path_after_drive.replace('\\', '/').lstrip('/')
    # 拼接为 Docker 挂载路径
    return f"/host_mnt/{drive_letter}/{unix_style_path}"


# 工具字符串
def truncate_path_from_data(volume_str: str) -> str:
    """
    处理形如 'D:/毕设/AIForge-backend/data/Model/57' 的路径，
    保留从 /data 开始的部分，加上权限后缀。
    """

    # 统一分隔符，防止反斜杠干扰（Windows）
    normalized_path = volume_str.replace('\\', '/')

    # 找到 /data 开始的位置
    index = normalized_path.lower().find('/data')
    if index == -1:
        raise ValueError("Path does not contain '/data'")

    # 截取从 /data 开始的路径并加上模式
    truncated = normalized_path[index:]
    return truncated
