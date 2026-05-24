from pydantic import BaseModel


class AuthUser(BaseModel):
    id: str
    email: str
    displayName: str
    role: str
    title: str
