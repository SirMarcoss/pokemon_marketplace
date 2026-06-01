from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)


    def __repr__(self) -> str:
        return f"<Category(id={self.id!r}, name={self.name!r}, slug={self.slug!r})>"