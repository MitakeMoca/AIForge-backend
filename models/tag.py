from tortoise import fields
from .basemodel import BaseModel


class Tag(BaseModel):
    tag_id = fields.IntField(pk=True)
    tag_name = fields.CharField(max_length=255)
    description = fields.TextField()

    class Meta:
        table = "tag"

    @staticmethod
    async def get_by_name(tag_name: str):
        # 获取Tag表中通过tag_name查询到的标签
        tag = await Tag.filter(tag_name=tag_name).first()
        return tag

    @staticmethod
    async def get_all_tags():
        return await Tag.all()

    @staticmethod
    async def get_all_tags_name():
        tags = await Tag.all().values('tag_name')
        tag_names = [tag['tag_name'] for tag in tags]
        return tag_names
