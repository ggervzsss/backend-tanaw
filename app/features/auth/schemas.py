from typing import Literal

from pydantic import BaseModel, Field

from app.features.accounts.schemas import AuthUser


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str
    loginScope: Literal["web", "enterprise"] = "web"


class LoginResponse(BaseModel):
    token: str
    user: AuthUser
