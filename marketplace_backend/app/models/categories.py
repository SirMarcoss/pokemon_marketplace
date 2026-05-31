from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Categories(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(nullable=False, unique=True)


    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, slug={self.slug!r}"