import docker
import os
from concurrent.futures import ThreadPoolExecutor

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

    def container_creator(self, image_name, project_id, gpu_needed, cpu_needed, port, model_path,
                          project_store_path, train_dataset_store_path, test_dataset_store_path, project_dao_impl):
        warnings = []
        container_name = f"project_{project_id}"

        # 检查资源是否足够
        if gpu_needed is not None and gpu_needed + self.gpu_use > self.gpu_max:
            warnings.append("GPU 资源不足，无法分配")
        if cpu_needed is not None and cpu_needed + self.cpu_use > self.cpu_max:
            warnings.append("CPU 资源不足，无法分配")
        if not self.search_image(image_name + ":latest"):
            warnings.append("镜像不存在")
        if container_name in self.container_name_to_id:
            warnings.append(f"容器 {container_name} 已存在")
            warnings.append("403")

        if not warnings:
            binds = {
                '/app/model': model_path,
                '/app/Project': project_store_path,
                '/app/Train_Dataset': train_dataset_store_path,
                '/app/Test_Dataset': test_dataset_store_path
            }

            try:
                container = self.docker_client.containers.create(
                    image_name,
                    name=container_name,
                    ports={80: port},  # 映射端口
                    volumes=binds
                )
                container.start()
                self.container_name_to_id[container_name] = container.id

                project_dao_impl.update_project_status_by_id(project_id, "wait")

                # 更新资源使用情况
                self.gpu_use += gpu_needed or 0
                self.cpu_use += cpu_needed or 0

                warnings.append(f"Success! Container Id 为 {container.id}")
                warnings.append("200")
            except docker.errors.DockerException as e:
                warnings.append(f"容器创建失败: {str(e)}")
                warnings.append("500")
        else:
            warnings.append("500")

        return warnings

    def image_creator(self, image_name, pathname):
        """创建镜像并返回状态"""
        if self.search_image(image_name):
            return ResultGenerator.gen_fail_result(message="镜像已存在")
        else:
            try:
                dockerfile_dir = os.path.abspath(pathname)

                self._build_image(dockerfile_dir, image_name)

                return 200  # 返回成功状态
            except Exception as e:
                print(f"镜像创建失败: {e}")
                return 500

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
