import tortoise.exceptions
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from core import config

router = APIRouter()
user_repository = UserRepository()  # Instantiate repository
auth_service = AuthService(user_repository)  # Inject repository into service


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register")
async def register(user: UserCreate):
    try:
        created_user = await auth_service.register_user(user.username, user.email, user.password)
    except tortoise.exceptions.IntegrityError:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"id": created_user.id, "username": created_user.username}


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    authenticated_user = await auth_service.authenticate_user(user.username, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": authenticated_user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}