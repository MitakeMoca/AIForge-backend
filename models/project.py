from tortoise import fields
from .basemodel import BaseModel


class Project(BaseModel):
    project_id = fields.IntField(pk=True)
    project_name = fields.CharField(max_length=255)
    description = fields.TextField()
    user_id = fields.CharField(max_length=255)
    status = fields.CharField(max_length=100)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)
    visibility = fields.CharField(max_length=100)
    model_id = fields.IntField()  # 外键关联Model
    train_dataset_id = fields.IntField()
    test_dataset_id = fields.IntField()
    store_path = fields.CharField(max_length=255)
    project_type = fields.CharField(max_length=100)

    class Meta:
        table = "project"
