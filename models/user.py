from dataclasses import asdict

from tortoise import fields, models
from tortoise.exceptions import DoesNotExist
from typing import List, Optional
from models.model import Model  # 确保 Model 已导入


class User(models.Model):
    user_id = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    level = fields.IntField(default=0)
    email = fields.CharField(max_length=255)
    image_id = fields.CharField(max_length=255, default=0)
    admin = fields.IntField(default=0)

    favor_models = fields.ManyToManyField('models.Model', related_name='users', through='favor')

    class Meta:
        table = "user"

    def dict(self):
        result = {field: getattr(self, field) for field in self.__dict__ if not field.startswith('_')}
        result.pop('favor_models', None)  # 移除密码字段
        return result

    # 获取所有用户
    @staticmethod
    async def all_users() -> List["User"]:
        users = await User.all()
        return users

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

    # 是否收藏模型
    @staticmethod
    async def is_favor(user_id: str, model_id: int) -> bool:
        user = await User.get_or_none(user_id=user_id).prefetch_related('favor_models')
        if not user:
            return False
        return await user.favor_models.filter(id=model_id).exists()

    # 添加收藏
    @staticmethod
    async def add_favor(user_id: str, model_id: int) -> bool:
        user = await User.get_or_none(user_id=user_id)
        model = await Model.get_or_none(id=model_id)
        if not user or not model:
            return False
        await user.favor_models.add(model)
        return True

    # 删除收藏
    @staticmethod
    async def delete_favor(user_id: str, model_id: int) -> bool:
        user = await User.get_or_none(user_id=user_id)
        model = await Model.get_or_none(id=model_id)
        if not user or not model:
            return False
        await user.favor_models.remove(model)
        return True

    # 获取用户收藏的所有模型ID
    @staticmethod
    async def get_favored_models_by_user_id(user_id: str) -> List[int]:
        user = await User.get_or_none(user_id=user_id).prefetch_related('favor_models')
        if not user:
            return []
        models = await user.favor_models.all()
        return [model.id for model in models]

    # 获取收藏某模型的所有用户ID
    @staticmethod
    async def get_users_who_favored_model(model_id: int) -> List[str]:
        model = await Model.get_or_none(id=model_id).prefetch_related('users')
        if not model:
            return []
        users = await model.users.all()
        return [user.user_id for user in users]

    # 判断收藏是否存在
    @staticmethod
    async def exists_favor(user_id: str, model_id: int) -> bool:
        return await User.is_favor(user_id, model_id)

    # 获取用户收藏数量
    @staticmethod
    async def count_favors_by_user_id(user_id: str) -> int:
        user = await User.get_or_none(user_id=user_id).prefetch_related('favor_models')
        if not user:
            return 0
        return await user.favor_models.all().count()

    # 获取某模型被收藏数量
    @staticmethod
    async def count_favors_by_model_id(model_id: int) -> int:
        model = await Model.get_or_none(id=model_id).prefetch_related('users')
        if not model:
            return 0
        return await model.users.all().count()
