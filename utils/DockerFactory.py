import docker
import os
from typing import List, Dict, Any
from fastapi import HTTPException
import asyncio

from utils.DockerCore import DockerCore


class DockerFactory:
    docker_factory: "DockerFactory" = None
    docker_client_pool: Dict[str, Any] = {}  # Mapping of host address to DockerCore instance
    hosts: List[str] = []

    def __init__(self):
        self.docker_factory = self
        self.client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        self.read_hosts("./resources/hosts.txt")  # Initialize hosts from file

    async def add_new_docker_client(self, host: str) -> int:
        """ Adds a new Docker client to the pool based on the provided host """
        if host:
            try:
                docker_core = DockerCore(host)
                await docker_core.load_docker_images()  # Assuming async version
                self.docker_client_pool[host] = docker_core
                return 200
            except Exception as e:
                print(f"Error adding Docker client for {host}: {e}")
                return 500
        return 500

    async def add_new_docker_clients(self, host_list: List[str]) -> List[int]:
        """ Adds a list of Docker clients asynchronously """
        results = []
        if host_list:
            self.hosts.extend(host_list)
            tasks = [self.add_new_docker_client(host) for host in host_list]
            results = await asyncio.gather(*tasks)
        else:
            results.append(404)
        return results

    async def hosts_to_string(self, pathname: str = "./resources/hosts.txt") -> None:
        """ Saves the list of hosts to the specified file """
        try:
            with open(pathname, 'w') as f:
                for host in self.hosts:
                    f.write(f"{host}\n")
        except Exception as e:
            print(f"Error writing to file {pathname}: {e}")

    def read_hosts(self, pathname: str = "./resources/hosts.txt") -> None:
        """ Reads hosts from the specified file """
        try:
            with open(pathname, 'r') as f:
                for line in f:
                    host = line.strip()
                    self.add_new_docker_client(host)
        except Exception as e:
            print(f"Error reading file {pathname}: {e}")