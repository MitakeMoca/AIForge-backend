import docker
import os
from typing import List
from fastapi import HTTPException
import asyncio


class ImageList:
    image_list: List[str] = []

    @classmethod
    def add_image(cls, image: str) -> None:
        """ Adds a Docker image to the list """
        if image and image not in cls.image_list:
            cls.image_list.append(image)

    @classmethod
    def remove_image(cls, image: str) -> bool:
        """ Removes a Docker image from the list """
        if image in cls.image_list:
            cls.image_list.remove(image)
            return True
        return False

    @classmethod
    def get_images(cls) -> List[str]:
        """ Returns a copy of the image list """
        return cls.image_list.copy()

    @classmethod
    def search_image(cls, image_name: str) -> bool:
        """ Searches for a specific image in the list """
        return image_name in cls.image_list

    @classmethod
    async def list_to_string(cls, pathname: str = "./resources/image.txt") -> None:
        """ Saves the image list to a file """
        try:
            with open(pathname, 'w') as file:
                for image in cls.image_list:
                    file.write(f"{image}\n")
        except Exception as e:
            print(f"Error writing to file {pathname}: {e}")

    @classmethod
    async def load_docker_images(cls, docker_core: "DockerCore") -> None:
        """ Loads images from a Docker instance into the image list """
        images = await docker_core.list_images()  # Assume list_images is async
        if images is not None:
            for image in images:
                cls.add_image(image if image else "untagged")