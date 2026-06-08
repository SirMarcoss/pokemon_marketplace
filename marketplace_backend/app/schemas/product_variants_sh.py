from decimal import Decimal
from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from typing import Optional
from app.models.product_variants import CardConditionEnum
from datetime import datetime


class ProductVariantCreate(BaseModel):
    product_id: int
    sku: str
    language: Optional[str] = Field(default=None, max_length=5)
    is_foil: bool
    is_first_edition: bool
    img_master_url: Optional[str] = None
    img_thumb_url: Optional[str] = None
    card_condition: Optional[CardConditionEnum] = None
    price_net_cents: int = Field(gt=0, description="price_net_cents must be greater than zero")
    stock: int = Field(ge=0, description="stock must be greater or equal then zero")


class ProductVariantUpdate(BaseModel):
    is_foil: Optional[bool] = None
    card_condition: Optional[CardConditionEnum] = None
    sku: Optional[str] = None
    img_master_url: Optional[str] = None
    img_thumb_url: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    price_net_cents: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None


class ProductVariantRead(BaseModel):
    id: int
    product_id: int
    sku: str
    language: Optional[str] = None
    is_foil: bool
    is_first_edition: bool
    version: int
    img_master_url: Optional[str] = None
    img_thumb_url: Optional[str] = None
    card_condition: Optional[CardConditionEnum] = None
    price_net_cents: int
    tax_rate: Decimal
    price_gross_cents: int
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)





