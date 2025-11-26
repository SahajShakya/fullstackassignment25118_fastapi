"""Authentication request/response models"""
from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    display_name: str = Field(..., min_length=2)


class UserLoginResponse(BaseModel):
    success: bool
    user_id: str = None
    username: str = None
    display_name: str = None
    access_token: str = None
    message: str


class UserRegisterResponse(BaseModel):
    success: bool
    user_id: str = None
    username: str = None
    display_name: str = None
    access_token: str = None
    message: str
