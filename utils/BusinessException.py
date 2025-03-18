from fastapi import HTTPException
from typing import Optional


class BusinessException(HTTPException):
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code

        super().__init__(status_code=status_code, detail=message)

    def get_error_code(self) -> str:
        return self.error_code
