from test_project.db.rdb import User, rdb_session_manager
from test_project.db.repositories.user import UserRepository
from test_project.exceptions import DuplicateEntryError


class UserManager:
    user_repo: UserRepository

    def __init__(self) -> None:
        self.user_repo = UserRepository(rdb_session_manager)

    @rdb_session_manager.transactional
    async def create_user(self, username: str, password: str) -> User:
        user = User(name=username, password=password)
        # check if there already exists the user naming the same
        if await self.user_repo.check_user_exists(user):
            raise DuplicateEntryError(f"user with the name {username} already exists")

        return await self.user_repo.create_user(user)

    @rdb_session_manager.transactional
    async def get_user(self, user_id: int) -> User:
        return await self.user_repo.get_user_by_id(user_id)


user_manager = UserManager()
