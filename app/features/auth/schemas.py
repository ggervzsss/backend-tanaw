from pydantic import BaseModel, EmailStr

from app.features.accounts.schemas import AuthUser


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: AuthUser
