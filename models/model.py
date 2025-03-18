from tortoise.exceptions import DoesNotExist
from tortoise import fields, models
from typing import List


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
    model_path = fields.CharField(max_length=255)
    user_id = fields.CharField(max_length=255)
    hypara_path = fields.CharField(max_length=255)
    tag = fields.CharField(max_length=255)

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
        model = await cls.get_or_none(id=model_id).prefetch_related('tags')
        if model:
            return [tag.tag_name for tag in model.tags]
        return []
