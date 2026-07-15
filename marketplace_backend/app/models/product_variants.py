from decimal import Decimal
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, declared_attr
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import CheckConstraint, ForeignKey, Computed, Index
from sqlalchemy.sql.sqltypes import Numeric, DateTime, Integer, Enum as SAEnum, Text
from datetime import datetime
from app.models.base import Base
import enum


class CardConditionEnum(enum.Enum):
    MINT = "mint"
    NEAR_MINT = "near_mint"
    EXCELLENT = "excellent"
    GOOD = "good"
    LIGHTLY_PLAYED = "lightly_played"
    PLAYED = "played"
    POOR = "poor"


class ProductVariant(Base):
    __tablename__ = "product_variants"

    # Valutazione "lazy": viene eseguito solo quando l'intera classe è pronta
    @declared_attr
    def __mapper_args__(cls):
        return {"version_id_col": cls.version}

    __table_args__ = (
        CheckConstraint("price_net_cents > 0", name="price_net_positivo"),
        CheckConstraint("tax_rate >=0 AND tax_rate <=100",
        name="tax_rate_valida"),
        CheckConstraint("stock >= 0", name="stock_non_negativo"),
        Index("idx_variants_catalog", "product_id", postgresql_where=text("is_active = true AND deleted_at IS NULL AND stock > 0")),
    )


    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(unique=True, nullable=False)
    language: Mapped[str] = mapped_column(server_default="IT")
    is_foil: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
    is_first_edition: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
    version: Mapped[int] = mapped_column(Integer,nullable=False, server_default="1")
    card_condition: Mapped[Optional[CardConditionEnum]] = mapped_column(
        SAEnum(
            CardConditionEnum,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            name="card_condition_enum",
        ),
        nullable=True,
    )
    price_net_cents: Mapped[int] = mapped_column(nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, server_default="22.00")

    # Computed column: price_gross_cents is never written manually.
    # The database calculates it automatically using price_net_cents and tax_rate.
    # Formula: gross = net * (1 + tax_rate / 100)
    # persisted=True means the value is physically stored once on insert/update,
    # rather than being recalculated on every read.
    price_gross_cents: Mapped[int] = mapped_column(Integer,
    Computed(
    "CAST(ROUND(CAST(price_net_cents AS NUMERIC) * (1 + tax_rate / 100.0)) AS INTEGER)",
    persisted=True
        ),
        nullable=False
    )
    stock: Mapped[int] = mapped_column(nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default=text("true"))
    img_master_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    img_thumb_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


    def __repr__(self) -> str:
        return (f"product_variant=(id={self.id!r}, product_id={self.product_id!r}, sku={self.sku!r},"
                f" language={self.language!r}, price_net_cents={self.price_net_cents!r},"
                f" price_gross_cents={self.price_gross_cents!r}")