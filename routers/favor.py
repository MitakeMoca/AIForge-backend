from fastapi import APIRouter

from models import User
from utils.ResultGenerator import ResultGenerator

favors = APIRouter()


@favors.get('/getFavoredModelsByUserId/{user_id}')
async def get_favored_models_by_user(user_id: str):
    models = await User.get_favored_models_by_user_id(user_id)
    return ResultGenerator.gen_success_result(data=models)
