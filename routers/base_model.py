from datetime import datetime

from pydantic import BaseModel

from test_project.db.rdb import User


class UserInfoModel(BaseModel):
    id: int
    name: str
    avatar: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserInfoModel":
        return cls(
            id=user.id,
            name=user.name,
            avatar=user.avatar,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
