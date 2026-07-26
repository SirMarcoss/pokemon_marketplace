from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from typing import Optional
from datetime import datetime
from app.schemas.product_variants_sh import ProductVariantRead


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: int
    expansion_id: Optional[int] = None


class ProductUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = None
    category_id: Optional[int] = None
    expansion_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductRead(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    category_id: int
    expansion_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class ProductDetailRead(BaseModel):
    """
    Schema composito per restituire un prodotto intero
    con tutto il suo array di varianti collegate.
    """
    product: ProductRead
    variants: list[ProductVariantRead]

    model_config = ConfigDict(from_attributes=True)
    # Questo serve per permettere a Pydantic di leggere oggetti SQLAlchemy