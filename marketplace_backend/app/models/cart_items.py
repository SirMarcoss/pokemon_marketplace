import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
from app.models.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="cart_qty_positiva"),

        # Vincolo fondamentale: impedisce duplicati dello stesso oggetto nello stesso carrello
        UniqueConstraint("cart_id", "variant_id", name="uq_cart_variant"),
    )

    # Integer è sufficiente e ottimizzato per tabelle pivot/relazionali interne
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Aggiunta esplicita del fuso orario
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


    def __repr__(self) -> str:
        return f"<CartItem(cart_id={self.cart_id!r}, variant_id={self.variant_id!r}, qty={self.quantity!r})>"