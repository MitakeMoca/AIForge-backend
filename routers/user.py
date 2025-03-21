from typing import Dict
from pydantic import BaseModel
import random
import string
from fastapi import APIRouter, HTTPException

from models import User
from utils.ResultGenerator import ResultGenerator

user = APIRouter()
verification_codes: Dict[str, str] = {}


# Pydantic 模型：请求体的结构
class VerificationRequest(BaseModel):
    email: str


class UserRegister(BaseModel):
    Email: str
    VerificationCode: str
    Password: str
    UserId: str


# 随机生成验证码的函数
def generate_verification_code() -> str:
    return ''.join(random.choices(string.digits, k=6))  # 生成6位数字验证码


@user.post('/sendVerificationCode')
async def send_verification_code(request: VerificationRequest):
    print(request.dict())
    email = request.email
    # 检查邮箱是否已经注册
    # 假设我们有一个数据库查询函数 `find_by_email()`，这里用假数据来模拟
    existing_user = await User.find_by_email(email)  # 假设这个是已注册的用户邮箱列表
    if existing_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 生成验证码
    code = generate_verification_code()
    print(f"验证码是: {code}")
    verification_codes[email] = code

    return {"message": "验证码已发送到邮箱"}


def is_verification_code_valid(email, verification_code):
    return verification_codes[email] == verification_code


@user.put('/')
async def register_by_email(params: UserRegister):
    email = params.Email
    verification_code = params.VerificationCode
    password = params.Password
    user_id = params.UserId

    # 验证邮箱是否已注册
    existing_users = await User.find_by_email(email)
    if existing_users:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 验证验证码
    if not is_verification_code_valid(email, verification_code):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    # 创建用户
    user_dict = {
        'user_id': user_id,
        'username': f"用户_{user_id}",
        'email': email,
        'password': password,
    }
    # 注册用户到数据库
    new_user = await User.add_user(user_dict)

    # 返回注册成功结果
    return ResultGenerator.gen_success_result(data=user_dict)


@user.get('/{user_id}/{password}')
async def login(user_id: str, password: str):
    user_dict = {
        'user_id': user_id,
        'password': password
    }

    print(user_dict)

    # 获取用户数据
    user_list = [await User.find_by_id(user_id)]
    print(user_list)

    if user_list[0] is None:
        user_list = [await User.find_by_email(user_id)]

    if len(user_list) != 0:
        if user_list[0].password == password:
            return ResultGenerator.gen_success_result(data={"user_id": user_list[0].user_id, "email": user_list[0].email})
        else:
            return ResultGenerator.gen_fail_result("密码错误")

    return ResultGenerator.gen_fail_result("无用户")


# 获取全部用户
@user.get('/')
async def get_all_users():
    all_users = await User.all_users()
    return ResultGenerator.gen_success_result(data=all_users)


# 删除某个用户
@user.delete('/{id}')
async def delete_user_by_id(id: str):
    ret = await User.delete_by_id(id)
    if ret:
        return ResultGenerator.gen_success_result(data="删除成功")
    return ResultGenerator.gen_fail_result(data="用户名不存在")
