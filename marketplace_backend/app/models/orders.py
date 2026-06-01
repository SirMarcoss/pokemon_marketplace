import enum
import uuid
from datetime import datetime
from typing import Any
from sqlalchemy import CheckConstraint, Enum as SAEnum, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func

from app.models.base import Base


class PaymentStatusEnum(enum.Enum):
    PENDING = 'pending'
    AUTHORIZED = 'authorized'  # Aggiunto per gestire il blocco fondi Stripe pre-cattura
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class FulfillmentStatusEnum(enum.Enum):
    UNFULFILLED = 'unfulfilled'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    READY_FOR_PICKUP = 'ready_for_pickup'  # Aggiunto per il ritiro in sede (negozio fisico)
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


class Order(Base):
    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint("total_amount_cents > 0", name="total_positivo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Mapped[uuid.UUID | None] è obbligatorio perché ondelete="SET NULL" rende la colonna nullabile
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Sostituzione dei campi flat (street, city, etc.) con JSONB per storicizzazione immutabile
    shipping_address: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    billing_address: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    total_amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)

    stripe_intent_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        SAEnum(PaymentStatusEnum), nullable=False, default=PaymentStatusEnum.PENDING
    )

    fulfillment_status: Mapped[FulfillmentStatusEnum] = mapped_column(
        SAEnum(FulfillmentStatusEnum), nullable=False, default=FulfillmentStatusEnum.UNFULFILLED
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Utilizzo esplicito di DateTime(timezone=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # onupdate=func.now() garantisce che l'ORM aggiorni il campo anche prima del commit finale nel DB
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        # Un __repr__ pulito evita di stampare JSON enormi nei log, limitandosi ai dati essenziali
        return (
            f"<Order(id={self.id!r}, email={self.customer_email!r}, "
            f"total_cents={self.total_amount_cents!r}, "
            f"payment={self.payment_status.value!r}, "
            f"fulfillment={self.fulfillment_status.value!r})>"
        )