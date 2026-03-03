from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    display_name: str | None = None
    role: str = "user"
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
