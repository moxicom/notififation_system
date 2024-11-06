import os

class Config:
    JWT_SECRET: str = os.getenv("JWT_SECRET", default="your_jwt_secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

config = Config()