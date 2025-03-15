from tortoise.models import Model


class BaseModel(Model):
    class Meta:
        abstract = True
