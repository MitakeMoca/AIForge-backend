from tortoise import fields
from .basemodel import BaseModel


class Model(BaseModel):
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
