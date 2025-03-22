from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import docker
import asyncio
from typing import List, Optional, Dict, Any

from utils.ResultGenerator import ResultGenerator

app = FastAPI()


class DockerCore:
    def __init__(self, docker_host: str = "tcp://localhost:2375"):
        self.client = docker.DockerClient(base_url=docker_host)
        self.container_name_to_id = {}
        self.gpu_max = 0
        self.gpu_used = 0
        self.cpu_max = 0
        self.cpu_used = 0
        self.initialize_container_map()

    def initialize_container_map(self):
        containers = self.client.containers.list(all=True)
        for container in containers:
            name = container.name
            container_id = container.id
            self.container_name_to_id[name] = container_id

    async def create_container(self, image_name: str, project_id: int, gpu_needed: Optional[int],
                               cpu_needed: Optional[int],
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
                container = self.client.containers.create(
                    image=image_name,
                    name=container_name,
                    ports={f"80/tcp": port},
                    volumes=volumes
                )
                container.start()
                self.container_name_to_id[container_name] = container.id
                project_dao.update_project_status_by_id(project_id, "wait")
                self.gpu_used += gpu_needed or 0
                self.cpu_used += cpu_needed or 0

                warnings.append(f"Success! Container ID is {container.id}")
                warnings.append("200")
            except Exception as e:
                warnings.append(str(e))
                warnings.append("500")
        return warnings

    def _image_exists(self, image_name: str) -> bool:
        return self.client.images.get(image_name) is not None

    async def build_image(self, image_name: str, dockerfile_path: str):
        if self._image_exists(image_name):
            return ResultGenerator.gen_fail_result(message="镜像已经存在")
        try:
            output = []
            for chunk in self.client.api.build(path=dockerfile_path, tag=image_name, rm=True):
                if isinstance(chunk, dict) and 'stream' in chunk:
                    output.append(chunk['stream'])
                elif isinstance(chunk, dict) and 'error' in chunk:
                    raise Exception(chunk['error'])
            return "\n".join(output)
        except Exception as e:
            return ResultGenerator.gen_fail_result(message=f"镜像创建失败{e}")

    async def check_container_status(self, container_name: str) -> str:
        if container_name not in self.container_name_to_id:
            raise HTTPException(status_code=404, detail=f"Container {container_name} does not exist")

        container = self.client.containers.get(self.container_name_to_id[container_name])
        return container.status

    async def container_log(self, container_name: str):
        if container_name not in self.container_name_to_id:
            raise HTTPException(status_code=404, detail=f"Container {container_name} does not exist")

        container = self.client.containers.get(self.container_name_to_id[container_name])
        logs = container.logs(stream=True)
        async for log in logs:
            print(log.decode("utf-8"))

    async def exec_container_log(self, project_id: int, command: str, project_dao: Any) -> List[str]:
        warnings = []
        container_name = f"project_{project_id}"
        try:
            container = self.client.containers.get(self.container_name_to_id[container_name])
            exec_log = container.exec_run(command)
            logs = exec_log.output.decode("utf-8")
            print(logs)

            project_dao.update_project_status_by_id(project_id, "running")
            warnings.append("200")
        except Exception as e:
            warnings.append(str(e))
            project_dao.update_project_status_by_id(project_id, "stopped")
            warnings.append("500")
        return warnings

    async def stop_container(self, project_id: int, project_dao: Any):
        container_name = f"project_{project_id}"
        try:
            container = self.client.containers.get(self.container_name_to_id[container_name])
            container.stop()
            container.remove()
            project_dao.update_project_status_by_id(project_id, "stopped")
            self.container_name_to_id.pop(container_name, None)
        except Exception as e:
            print(f"Error stopping container: {e}")

    def list_images(self) -> List[str]:
        images = self.client.images.list()
        return [image.tags[0] if image.tags else "untagged" for image in images]


docker_core = DockerCore()


# FastAPI routes
class DockerRequest(BaseModel):
    image_name: str
    project_id: int
    gpu_needed: Optional[int] = None
    cpu_needed: Optional[int] = None
    port: int
    model_path: str
    project_store_path: str
    train_dataset_store_path: str
    test_dataset_store_path: str


@app.post("/create-container")
async def create_container(request: DockerRequest, project_dao: Any):
    result = await docker_core.create_container(
        image_name=request.image_name,
        project_id=request.project_id,
        gpu_needed=request.gpu_needed,
        cpu_needed=request.cpu_needed,
        port=request.port,
        model_path=request.model_path,
        project_store_path=request.project_store_path,
        train_dataset_store_path=request.train_dataset_store_path,
        test_dataset_store_path=request.test_dataset_store_path,
        project_dao=project_dao
    )
    return {"result": result}


@app.post("/build-image")
async def build_image(image_name: str, dockerfile_path: str):
    output = await docker_core.build_image(image_name, dockerfile_path)
    return {"output": output}


@app.get("/check-container-status/{container_name}")
async def check_container_status(container_name: str):
    status = await docker_core.check_container_status(container_name)
    return {"status": status}


@app.get("/container-log/{container_name}")
async def container_log(container_name: str):
    await docker_core.container_log(container_name)
    return {"status": "Logs printed"}


@app.post("/exec-container-log/{project_id}")
async def exec_container_log(project_id: int, command: str, project_dao: Any):
    result = await docker_core.exec_container_log(project_id, command, project_dao)
    return {"result": result}


@app.post("/stop-container/{project_id}")
async def stop_container(project_id: int, project_dao: Any):
    await docker_core.stop_container(project_id, project_dao)
    return {"status": "stopped"}


@app.get("/list-images")
async def list_images():
    images = docker_core.list_images()
    return {"images": images}
