from typing import Optional, Any
from fastapi import HTTPException


class ResultGenerator:
    # 定义常量
    RESULT_CODE_SUCCESS = 200
    RESULT_CODE_SERVER_ERROR = 500
    RESULT_CODE_NOT_FOUND = 404

    DEFAULT_SUCCESS_MESSAGE = "SUCCESS"
    DEFAULT_FAIL_MESSAGE = "FAIL"
    DEFAULT_NOT_FOUND_MESSAGE = "Not Found"

    @staticmethod
    def gen_success_result(message: str = DEFAULT_SUCCESS_MESSAGE, data: Optional[Any] = None) -> dict:
        """ 生成成功的响应 """
        return {
            "resultCode": ResultGenerator.RESULT_CODE_SUCCESS,
            "message": message,
            "data": data
        }

    @staticmethod
    def gen_fail_result(message: str = DEFAULT_FAIL_MESSAGE, data: Optional[Any] = None) -> dict:
        """ 生成失败的响应 """
        return {
            "resultCode": ResultGenerator.RESULT_CODE_SERVER_ERROR,
            "message": message,
            "data": data
        }

    @staticmethod
    def gen_error_result(code: int, message: str) -> dict:
        """ 生成自定义错误码的响应 """
        return {
            "resultCode": code,
            "message": message,
            "data": None
        }

    @staticmethod
    def gen_not_found_result(message: str = DEFAULT_NOT_FOUND_MESSAGE, data: Optional[Any] = None) -> dict:
        """ 生成未找到的响应 """
        return {
            "resultCode": ResultGenerator.RESULT_CODE_NOT_FOUND,
            "message": message,
            "data": data
        }
