from tortoise import fields
from .basemodel import BaseModel


class Dataset(BaseModel):
    dataset_id = fields.IntField(pk=True)
    project_id = fields.IntField()
    dataset_name = fields.CharField(max_length=255)  # DataSetName
    data_url = fields.CharField(max_length=255)  # DataUrl
    data_type = fields.CharField(max_length=100)  # DataType
    data_size = fields.FloatField()  # DataSize
    label = fields.CharField(max_length=255)  # Label
    user_id = fields.CharField(max_length=255)  # UserId
    introduction = fields.TextField()  # Introduction
    public = fields.IntField(default=0)  # Public，默认为0
    models = fields.ManyToManyField('models.Model', related_name='datasets', through='md')

    class Meta:
        table = "dataset"
