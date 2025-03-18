from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

# 使用 TypeVar 来支持泛型
T = TypeVar('T')


class Result(BaseModel, Generic[T]):
    result_code: int
    message: str
    data: Optional[T] = None  # 允许 data 为 None

    def __init__(self, result_code: int, message: str, data: Optional[T] = None):
        super().__init__(result_code=result_code, message=message, data=data)

    def __str__(self):
        return f"Result(result_code={self.result_code}, message={self.message}, data={self.data})"