from typing import Optional
from sqlalchemy import DateTime, text, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey, Index
from sqlalchemy.sql.functions import func
from datetime import datetime
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"


    __table_args__ = (
        Index("idx_products_catalog", "id", postgresql_where=text("is_active = true AND deleted_at IS NULL")),
    )


    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    expansion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("expansions.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default=text("false"))
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
        return (
            f"<Product(id={self.id!r}, title={self.title!r}, slug={self.slug!r}, "
            f"category_id={self.category_id!r}, expansion_id={self.expansion_id!r}, "
            f"is_active={self.is_active!r})>"
        )