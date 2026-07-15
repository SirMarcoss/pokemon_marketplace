from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class CartItemBaseCreate(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")


class CartItemBaseUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0, description="Quantity must be greater than zero")


class CartItemBaseRead(BaseModel):
    id: int
    cart_id: UUID
    variant_id: int
    quantity: int
    added_at: datetime


    model_config = ConfigDict(from_attributes=True)