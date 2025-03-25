from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist


class Dataset(Model):
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
    likes = fields.IntField(default=0)
    models = fields.ManyToManyField('models.Model', related_name='datasets', through='md')

    class Meta:
        table = "dataset"  # 对应数据库中的 dataset 表

    @classmethod
    async def find_by_id(cls, dataset_id: int):
        """根据数据集 ID 查找数据集"""
        try:
            dataset = await cls.get(dataset_id=dataset_id)
            return dataset
        except DoesNotExist:
            return None

    @classmethod
    async def add_dataset(cls, dataset_data: dict):
        """添加数据集"""
        dataset = await cls.create(**dataset_data)
        return dataset

    @classmethod
    async def update_by_id(cls, dataset_id: int, dataset_data: dict):
        """根据 ID 更新数据集"""
        try:
            dataset = await cls.get(dataset_id=dataset_id)
            for field, value in dataset_data.items():
                setattr(dataset, field, value)
            await dataset.save()
            return dataset
        except DoesNotExist:
            return None

    @classmethod
    async def delete_by_id(cls, dataset_id: int):
        """根据 ID 删除数据集"""
        try:
            dataset = await cls.get(dataset_id=dataset_id)
            await dataset.delete()
            return True
        except DoesNotExist:
            return False

    @classmethod
    async def find_all(cls):
        """获取所有数据集"""
        return await cls.all()

    @classmethod
    async def find_by_user_id(cls, user_id: str):
        """根据用户 ID 查找数据集"""
        return await cls.filter(user_id=user_id)

    @classmethod
    async def find_all_md(cls):
        """获取 MD 表中的所有记录"""
        # 使用 raw SQL 查询 MD 表中的所有数据
        return await cls.raw('SELECT * FROM MD')

    @classmethod
    async def set_public_by_id(cls, dataset_id: int):
        """根据数据集 ID 设置数据集为公开"""
        try:
            dataset = await cls.get(dataset_id=dataset_id)
            dataset.public = 1
            await dataset.save()
            return True
        except DoesNotExist:
            return False

    @classmethod
    async def find_public_datasets(cls):
        """获取所有公开数据集"""
        return await cls.filter(public=1)

    @classmethod
    async def search_public_datasets(cls, keyword: str):
        """根据关键字搜索公开数据集"""
        return await cls.filter(public=1).filter(
            (cls.dataset_name.contains(keyword)) | (cls.label.contains(keyword))
        )

    @classmethod
    async def find_max_dataset_id(cls):
        """查找数据集最大 ID"""
        dataset = await cls.all().order_by('-dataset_id').first()
        return dataset.dataset_id if dataset else 0

    @classmethod
    async def update_dataset_url(cls, dataset_id: int, data_url: str):
        """根据数据集 ID 更新 URL"""
        try:
            dataset = await cls.get(dataset_id=dataset_id)
            dataset.data_url = data_url
            await dataset.save()
            return True
        except DoesNotExist:
            return False
