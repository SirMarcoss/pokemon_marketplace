import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, ForeignKey, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import func
from app.models.base import Base


class Cart(Base):
    __tablename__ = "carts"


    __table_args__ = (
        # Un carrello DEVE appartenere a un utente loggato OPPURE a una sessione guest.
        CheckConstraint(
            "(user_id IS NOT NULL) <>  (session_id IS NOT NULL)",
            name="cart_owner_check"
        ),
    )


    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=True
    )
    # Nullable (Utente loggato potrebbe non averlo), limitato a 255 caratteri
    session_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


    def __repr__(self) -> str:
        return f"<Cart(id={self.id!r}, user_id={self.user_id!r}, session_id={self.session_id!r})>"