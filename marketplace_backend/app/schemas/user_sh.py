from pydantic.main import BaseModel
from pydantic.types import EmailStr
from pydantic.config import ConfigDict
from pydantic.fields import Field
from typing import Optional
from app.models.user import UserRoleEnum
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class UserUpdate(BaseModel):
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)


class UserAdminUpdate(BaseModel):
    role: Optional[UserRoleEnum] = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRoleEnum
    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(from_attributes=True)