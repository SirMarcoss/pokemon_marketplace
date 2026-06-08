from decimal import Decimal
from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from uuid import UUID
from typing import Optional
from datetime import datetime


class OrderItemRead(BaseModel):
    id: int
    order_id: UUID
    variant_id: Optional[int] = None
    quantity: int
    product_name_at_purchase: str
    sku_at_purchase: str
    price_net_cents_at_purchase: int
    tax_rate_at_purchase: Decimal
    price_gross_cents_at_purchase: int
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)

