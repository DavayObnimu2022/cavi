from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class UserAuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None