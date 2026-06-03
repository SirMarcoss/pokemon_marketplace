from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from typing import Optional
from datetime import datetime


class ProductsCreate(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    category_id: int
    expansion_id: Optional[int] = None


class ProductsUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    category_id: Optional[int] = None
    expansion_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductsRead(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    category_id: int
    expansion_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)