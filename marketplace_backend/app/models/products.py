from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, func
from datetime import datetime
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[Optional[str]]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"))
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    
    def __repr__(self) -> str:
        return (f"User(id={self.id!r}, title={self.title!r}, slug{self.slug!r}, category_id={self.category_id!r},"
                f"is_active={self.is_active!r}, created_at={self.created_at!r}, updated_at{self.updated_at!r}")