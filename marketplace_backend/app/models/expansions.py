from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Expansion(Base):
    __tablename__ = "expansions"

    # Specificare Integer è una best practice per leggibilità in SQLAlchemy 2.0
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True #O(log N) con index al posto di O(N)
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)


    def __repr__(self) -> str:
        return (
            f"<Expansion(id={self.id!r}, category_id={self.category_id!r}, "
            f"name={self.name!r}, release_date={self.release_date!r}, "
            f"total_cards={self.total_cards!r})>"
        )