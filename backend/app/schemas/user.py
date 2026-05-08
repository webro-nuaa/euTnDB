from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    institution: Optional[str] = None
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    institution: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: str
    institution: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    user: UserResponse
