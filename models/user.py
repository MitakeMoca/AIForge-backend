from tortoise import fields, models
from tortoise.exceptions import DoesNotExist
from typing import List, Optional


class User(models.Model):
    user_id = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    level = fields.IntField(default=0)
    email = fields.CharField(max_length=255)
    image_id = fields.CharField(max_length=255)
    admin = fields.IntField(default=0)
    favor_models = fields.ManyToManyField('models.Model', related_name='users', through='favor')

    class Meta:
        table = "user"

    # 获取所有用户
    @staticmethod
    async def all_users() -> List["User"]:
        return await User.all()

    # 根据ID查询
    @staticmethod
    async def find_by_id(user_id: str) -> Optional["User"]:
        try:
            return await User.get(user_id=user_id)
        except DoesNotExist:
            return None

    # 根据Email查询
    @staticmethod
    async def find_by_email(email: str) -> Optional["User"]:
        try:
            return await User.get(email=email)
        except DoesNotExist:
            return None

    # 添加用户
    @staticmethod
    async def add_user(user_data: dict) -> "User":
        user = await User.create(**user_data)
        return user

    # 更新用户
    @staticmethod
    async def update_by_id(user_id: str, update_data: dict) -> bool:
        updated = await User.filter(user_id=user_id).update(**update_data)
        return updated > 0

    # 删除用户
    @staticmethod
    async def delete_by_id(user_id: str) -> bool:
        deleted = await User.filter(user_id=user_id).delete()
        return deleted > 0
