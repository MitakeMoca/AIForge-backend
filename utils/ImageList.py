import os


class ImageList:
    # 静态变量：保存镜像列表
    image_list = []

    # 添加镜像
    @staticmethod
    def add_image(image):
        if image and image.strip():  # 确保 image 不为空或空白
            ImageList.image_list.append(image)

    # 移除镜像
    @staticmethod
    def remove_image(image):
        if image in ImageList.image_list:
            ImageList.image_list.remove(image)
            return True
        return False

    # 获取镜像列表
    @staticmethod
    def get_images():
        return list(ImageList.image_list)  # 返回一个副本以保护内部状态

    # 搜索镜像
    @staticmethod
    def search_image(image_name):
        return image_name in ImageList.image_list

    # 将镜像列表写入文件
    @staticmethod
    def list_to_string(pathname=None):
        if pathname is None:
            pathname = './resource/image.txt'

        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(pathname), exist_ok=True)

        with open(pathname, 'w') as writer:
            for image in ImageList.image_list:
                writer.write(image + '\n')

    # 从 DockerCore 读取镜像并加载
    @staticmethod
    def load_docker_images(docker_core):
        images = docker_core.list_images()
        if not images:
            return
        for image in images:
            ImageList.add_image(image if image.strip() else "untagged")
