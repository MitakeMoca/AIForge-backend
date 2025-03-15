from tortoise import fields
from .basemodel import BaseModel


class Hypara(BaseModel):
    hypara_id = fields.CharField(max_length=255, pk=True)
    store_path = fields.CharField(max_length=255)
    project_id = fields.IntField()

    class Meta:
        table = "hypara"
