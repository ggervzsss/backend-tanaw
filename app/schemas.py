from pydantic import BaseModel, EmailStr


class AuthUser(BaseModel):
    id: str
    email: str
    displayName: str
    role: str
    title: str


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: AuthUser
