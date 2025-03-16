from tortoise import fields, models
from tortoise.exceptions import DoesNotExist


class Hypara(models.Model):
    hypara_id = fields.CharField(max_length=255, pk=True)
    store_path = fields.CharField(max_length=255)
    project_id = fields.IntField()

    class Meta:
        table = "hypara"  # 指定对应的数据库表名

    @classmethod
    async def find_by_project_id(cls, project_id: int):
        """根据项目 ID 查找所有的 StorePath"""
        return await cls.filter(project_id=project_id).values_list('store_path', flat=True)

    @classmethod
    async def add_or_update_hypara(cls, hypara: 'Hypara'):
        """根据 ProjectId 更新或插入 Hypara 记录"""
        try:
            # 尝试查找是否存在该 ProjectId 的记录
            existing_hypara = await cls.get(project_id=hypara.project_id)
            # 如果存在，则更新
            existing_hypara.store_path = hypara.store_path
            await existing_hypara.save()
            return True
        except DoesNotExist:
            # 如果没有该记录，则插入新记录
            await cls.create(project_id=hypara.project_id, store_path=hypara.store_path)
            return True
