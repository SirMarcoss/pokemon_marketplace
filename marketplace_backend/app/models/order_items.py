from datetime import datetime
from decimal import Decimal
import uuid
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import  String, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from sqlalchemy.sql.schema import CheckConstraint, ForeignKey
from  sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime



class OrderItem(Base):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="order_qty_positiva"),
        CheckConstraint("price_net_cents_at_purchase > 0", name="snap_net_positivo"),
        CheckConstraint("price_gross_cents_at_purchase > 0", name="snap_gross_positivo"),
    )


    id: Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[uuid.UUID]= mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False)
    variant_id: Mapped[Optional[int]]= mapped_column(ForeignKey("product_variants.id", ondelete="SET NULL"))
    quantity: Mapped[int]= mapped_column(nullable=False)
    product_name_at_purchase: Mapped[str]= mapped_column(String(255), nullable=False)
    sku_at_purchase:  Mapped[str]= mapped_column(String(100), nullable=False)
    price_net_cents_at_purchase: Mapped[int]= mapped_column(nullable=False)
    tax_rate_at_purchase: Mapped[Decimal]= mapped_column(Numeric(5, 2), nullable=False)
    price_gross_cents_at_purchase: Mapped[int]= mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)


    def __repr__(self) -> str:
        return (f"order_items(id={self.id!r}, order_id={self.order_id!r}, variant_id={self.variant_id!r}, "
                f"quantity={self.quantity!r}, product_name={self.product_name_at_purchase!r}, "
                f"sku={self.sku_at_purchase!r}, price_net={self.price_net_cents_at_purchase!r}, "
                f"tax_rate={self.tax_rate_at_purchase!r}, price_gross={self.price_gross_cents_at_purchase!r}, "
                f"created_at={self.created_at!r})")