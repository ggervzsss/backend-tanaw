from pydantic import BaseModel, Field

from app.features.accounts.schemas import AuthUser


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str


class LoginResponse(BaseModel):
    token: str
    user: AuthUser
