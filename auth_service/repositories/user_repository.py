from models.user import User
from tortoise.exceptions import DoesNotExist

class UserRepository:
    async def create_user(self, username: str, email: str, password: str) -> User:
        user = await User.create(username=username, email=email, password=password)
        return user

    async def get_user_by_username(self, username: str) -> User:
        try:
            return await User.get(username=username)
        except DoesNotExist:
            return None
