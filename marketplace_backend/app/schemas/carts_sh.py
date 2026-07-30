from app.schemas.cart_items_sh import CartItemDetailRead
from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class CartBaseRead(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    items: list[CartItemDetailRead] = Field(default_factory=list) #receives a list containing the products in the cart
    # default factory create a new list for each instance of CartBaseRead, preventing shared mutable state between instances

    model_config = ConfigDict(from_attributes=True)
