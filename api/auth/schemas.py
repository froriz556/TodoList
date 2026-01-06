from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserCreate):
    pass


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
