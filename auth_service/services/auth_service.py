from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from models.user import User
from core import config
from repositories.user_repository import UserRepository
import hashlib


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()  # Use a stronger hash in production

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.ALGORITHM)
        return encoded_jwt

    async def register_user(self, username: str, email: str, password: str) -> User:
        hashed_password = self.hash_password(password)
        return await self.user_repository.create_user(username, email, hashed_password)

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.user_repository.get_user_by_username(username)
        if user and user.password == self.hash_password(password):
            return user
        return None

    async def validate_token(self, token: str):
        jwt.decode(token, config.JWT_SECRET, algorithms=[config.ALGORITHM])