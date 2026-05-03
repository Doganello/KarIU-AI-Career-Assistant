from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserRegister(BaseModel):
    email:    EmailStr
    password: str


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserRead(BaseModel):
    id:         int
    email:      str
    role:       str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"