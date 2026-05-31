from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import CheckConstraint, ForeignKey, Computed
from sqlalchemy.sql.sqltypes import Numeric
from datetime import datetime
from app.models.base import Base


class ProductVariants(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    sku: Mapped[str] = mapped_column(unique=True, nullable=False)
    size: Mapped[Optional[str]]
    color: Mapped[Optional[str]]
    price_net_cents: Mapped[int] = mapped_column(
        CheckConstraint("price_net_cents > 0", name="price_net_positivo"),
        nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        CheckConstraint("tax_rate >=0 AND tax_rate <=100",
        name="tax_rate_valida"), nullable=False, default=22.0)

    # Computed column: price_gross_cents is never written manually.
    # The database calculates it automatically using price_net_cents and tax_rate.
    # Formula: gross = net * (1 + tax_rate / 100)
    # persisted=True means the value is physically stored once on insert/update,
    # rather than being recalculated on every read.
    price_gross_cents: Mapped[int] = mapped_column(Computed(
    "CAST(ROUND(price_net_cents * (1 + tax_rate / 100.0)) AS INT)",
    persisted=True
))
    stock: Mapped[int] = mapped_column(
        CheckConstraint("stock >= 0", name="stock_non_negativo"),nullable=False,default=0)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    img_master_url: Mapped[Optional[str]]
    img_thumb_url: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())


    def __repr__(self) -> str:
        return (f"id(id={self.id!r}, product_id={self.product_id!r}, sku{self.sku!r}, size={self.size!r},"
                f"color={self.color!r}, price_net_cents={self.price_net_cents!r}, taxe_rate{self.tax_rate!r}"
                f"price_gross_cents={self.price_gross_cents!r}, stock={self.stock!r}, is_active{self.is_active!r}"
                f"img_master_url={self.img_master_url!r}, img_thumb_url={self.img_thumb_url!r},"
                f" created_at{self.created_at!r}, updated_at{self.updated_at!r}")