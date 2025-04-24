from tortoise.exceptions import DoesNotExist
from tortoise import fields, models
from typing import List, Optional

from .tag import Tag


class Model(models.Model):
    id = fields.IntField(pk=True)
    model_name = fields.CharField(max_length=255)
    model_date = fields.DatetimeField(auto_now_add=True)
    model_description = fields.TextField()
    model_overview_markdown = fields.TextField()
    model_run_count = fields.IntField(default=0)
    model_view_count = fields.IntField(default=0)
    frame = fields.CharField(max_length=255)
    image_id = fields.IntField()
    pub = fields.IntField()
    model_path = fields.CharField(max_length=255, default='')
    user_id = fields.CharField(max_length=255)
    hypara_path = fields.CharField(max_length=255)
    tag = fields.CharField(max_length=255)
    secret_key = fields.CharField(max_length=255, default='MitakeMoca')

    class Meta:
        table = "model"

    @classmethod
    async def add_model(cls, model_data: dict) -> 'Model':
        """插入模型数据"""
        model = await cls.create(**model_data)
        return model

    @classmethod
    async def update_model(cls, model_id: int, model_data: dict) -> bool:
        """更新模型数据"""
        try:
            model = await cls.get(id=model_id)
            for key, value in model_data.items():
                setattr(model, key, value)
            await model.save()
            return True
        except DoesNotExist:
            return False

    @classmethod
    async def delete_model(cls, model_id: int) -> bool:
        """删除模型"""
        try:
            model = await cls.get(id=model_id)
            await model.delete()
            return True
        except DoesNotExist:
            return False

    @classmethod
    async def find_all(cls) -> List['Model']:
        """获取所有模型"""
        return await cls.all()

    @classmethod
    async def find_by_id(cls, model_id: int):
        """根据模型 ID 查找模型"""
        try:
            return await cls.get(id=model_id)
        except DoesNotExist:
            return None

    @classmethod
    async def increment_model_view_count(cls, model_id: int) -> bool:
        """增加模型浏览量"""
        try:
            model = await cls.get(id=model_id)
            model.model_view_count += 1
            await model.save()
            return True
        except DoesNotExist:
            return False

    # 查找所有公开模型
    @classmethod
    async def find_all_public(cls):
        return await cls.filter(pub=1).all()

    # 查找所有私有模型
    @classmethod
    async def find_all_private(cls):
        return await cls.filter(pub=0).all()

    # 查找所有待审核模型
    @classmethod
    async def find_all_waiting(cls):
        return await cls.filter(pub=2).all()

    # 按时间排序获取公开模型
    @classmethod
    async def find_all_public_sorted_by_time(cls):
        return await cls.filter(pub=1).order_by('-model_date').all()

    # 按浏览量排序获取公开模型
    @classmethod
    async def find_all_public_sorted_by_view(cls):
        return await cls.filter(pub=1).order_by('-model_view_count').all()

    @classmethod
    async def find_public_by_id(cls, model_id: int):
        return await cls.get_or_none(id=model_id, pub=1)

    @classmethod
    async def set_private(cls, model_id: int):
        model = await cls.get_or_none(id=model_id)
        if model:
            model.pub = 0
            await model.save()
            return True
        return False

    @classmethod
    async def set_public(cls, model_id: int):
        model = await cls.get_or_none(id=model_id)
        if model:
            model.pub = 1
            await model.save()
            return True
        return False

    @classmethod
    async def set_waiting(cls, model_id: int):
        model = await cls.get_or_none(id=model_id)
        if model:
            model.pub = 2
            await model.save()
            return True
        return False

    @classmethod
    async def get_tags_by_model_id(cls, model_id: int):
        model = await Model.get(id=model_id)
        if model and model.tag:
            return [tag.strip() for tag in model.tag.split(',') if tag.strip()]
        return []

    # 获取公开模型路径
    @classmethod
    async def find_public_model_path_by_id(cls, model_id: int) -> Optional[str]:
        model = await cls.filter(id=model_id, pub=1).first()
        return model.model_path if model else None

    # 根据 tag_name 获取模型列表（JOIN tag_model -> 模拟通过 Tag 关联）
    @classmethod
    async def get_models_by_tag_name(cls, tag_name: str) -> List['Model']:
        models = await Model.filter(tag__icontains=tag_name).all()
        return models

    # 判断模型是否属于用户
    @classmethod
    async def is_model_belongs_to_user(cls, user_id: str, model_id: int) -> bool:
        return await cls.filter(id=model_id, user_id=user_id).exists()

    # 获取指定用户的所有模型
    @classmethod
    async def get_models_by_user_id(cls, user_id: str) -> List['Model']:
        return await cls.filter(user_id=user_id).all()

    # 模型名称模糊搜索 (公开模型)
    @classmethod
    async def fuzzy_search_by_name(cls, model_name: str) -> List['Model']:
        return await cls.filter(model_name__icontains=model_name, pub=1).all()

    # 模型架构模糊搜索 (公开模型)
    @classmethod
    async def fuzzy_search_by_frame(cls, model_architecture: str) -> List['Model']:
        return await cls.filter(frame__icontains=model_architecture, pub=1).all()

    # 模型描述模糊搜索 (公开模型)
    @classmethod
    async def fuzzy_search_by_description(cls, model_description: str) -> List['Model']:
        return await cls.filter(model_description__icontains=model_description, pub=1).all()

    # 获取 HyparaPath
    @classmethod
    async def get_hypara_path_by_model_id(cls, model_id: int) -> Optional[str]:
        model = await cls.filter(id=model_id).first()
        return model.hypara_path if model else None

    # 给模型添加标签
    @classmethod
    async def add_tag_to_model(cls, model_id: int, tag_name: str) -> bool:
        print(model_id, tag_name)
        # 查找 Tag 表中是否有对应 tag
        tag = await Tag.get_by_name(tag_name)
        if not tag:
            return False
        # 模拟原 tag_model 表插入 (可以通过直接插入字符串 tag 字段)
        model = await cls.get_or_none(id=model_id)
        if not model:
            return False
        # 更新 model.tag 字段，假设逗号分隔
        if model.tag:
            tag_list = str(model.tag).split(",")
            if tag_name not in tag_list:
                tag_list.append(tag_name)
            model.tag = ",".join(tag_list)
        else:
            model.tag = tag_name
        await model.save()
        return True

    async def update_model_path(self, model_path: str):
        self.model_path = model_path
        await self.save()
