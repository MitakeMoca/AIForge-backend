import logging

from pydantic import BaseModel

from test_project.commons import Response, ResponseCode
from test_project.routers import CustomAPIRouter
from test_project.routers.base_model import UserInfoModel
from test_project.services.user import user_manager

logger = logging.getLogger(__name__)

router = CustomAPIRouter(prefix="/users", tags=["User Group"])


class UserCreateRequestDTO(BaseModel):
    name: str
    password: str


class UserCreateResponseDTO(BaseModel):
    user: UserInfoModel


@router.post("", response_model=Response[UserCreateResponseDTO])
async def create_user(request: UserCreateRequestDTO) -> Response[UserCreateResponseDTO]:
    user = await user_manager.create_user(request.name, request.password)
    return ResponseCode.OK.to_response(data=UserCreateResponseDTO(user=UserInfoModel.from_user(user)))
