"""
demo dependencies for fastapi
"""

# from typing import Annotated, Optional
#
# import jwt
# from fastapi import Depends, status
# from fastapi.security import OAuth2PasswordBearer
# from jwt.exceptions import InvalidTokenError
#
# from commons import AuthedUser
# from config import JWT_ALGORITHM, JWT_SECRET_KEY
# from exceptions import HTTPException
#
# _bearer_token_scheme = OAuth2PasswordBearer(tokenUrl="token")
#
#
# async def _parse_jwt_token(token: str) -> Optional[int]:
#     payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
#     id_str: str = payload.get("sub")
#     try:
#         return int(id_str)
#     except ValueError:
#         return None
#
#
# async def get_user(token: Annotated[str, Depends(_bearer_token_scheme)]) -> AuthedUser:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         content="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         user_id = await _parse_jwt_token(token)
#     except InvalidTokenError:
#         raise credentials_exception
#     if user_id is None:
#         raise credentials_exception
#     return AuthedUser(id=user_id)
