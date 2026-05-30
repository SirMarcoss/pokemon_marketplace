import enum
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import  String, func, UUID, Integer
from app.models.base import Base
from sqlalchemy.sql.schema import CheckConstraint, ForeignKey
from datetime import datetime
from typing import Optional


class payment_status_enum(enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'


class fulfillment_status_enum(enum.Enum):
    UNFULFILLED = 'unfulfilled'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


class orders(Base):
    __tablename__ = "orders"
    

    __table_args__ = (
        CheckConstraint("total_amount_cents > 0", name="total_positivo"),
    )


    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    shipping_street: Mapped[str] = mapped_column(String(255), nullable=False)
    shipping_city: Mapped[str] = mapped_column(String(255), nullable=False)
    shipping_zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    shipping_province: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_country: Mapped[str] = mapped_column(String(100), nullable=False, default='Italia')
    total_amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stripe_intent_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    payment_status: Mapped[payment_status_enum] = mapped_column(nullable=False, default=payment_status_enum.PENDING)
    fulfillment_status: Mapped[fulfillment_status_enum] = mapped_column(nullable=False, default=fulfillment_status_enum.UNFULFILLED)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self)->str:
        return (f"id={self.id!r}, customer_email={self.customer_email!r}, customer_name={self.customer_name!r},"
                f"shipping street={self.shipping_street!r}, shipping_city={self.shipping_city!r}, shipping_zip_code={self.shipping_zip_code!r},"
                f"shipping_province={self.shipping_province!r}, shipping_country={self.shipping_country!r}, total_amount_cents={self.total_amount_cents!r},"
                f"stripe_intent_id={self.stripe_intent_id!r}, payment_status={self.payment_status!r}, fulfillment_status={self.fulfillment_status!r},"
                f"user_id={self.user_id!r}, created_at={self.created_at!r}") 