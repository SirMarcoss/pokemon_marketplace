from app.schemas.cart_items_sh import CartItemBaseRead
from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class CartBaseRead(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    session_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    items: list[CartItemBaseRead] = [] #receives a list containing the products in the cart

    model_config = ConfigDict(from_attributes=True)
