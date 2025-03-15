from tortoise import fields
from .basemodel import BaseModel


class Tag(BaseModel):
    tag_id = fields.IntField(pk=True)
    tag_name = fields.CharField(max_length=255)
    description = fields.TextField()

    class Meta:
        table = "tag"
        