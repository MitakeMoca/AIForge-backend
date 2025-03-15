from tortoise import fields
from .basemodel import BaseModel


class User(BaseModel):
    user_id = fields.CharField(max_length=255, pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    level = fields.IntField(default=0)
    email = fields.CharField(max_length=255)
    image_id = fields.CharField(max_length=255)
    admin = fields.IntField()
    favor_models = fields.ManyToManyField('models.Model', related_name='users', through='favor')

    class Meta:
        table = "user"
