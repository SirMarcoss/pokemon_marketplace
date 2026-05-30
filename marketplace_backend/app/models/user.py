from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime
from sqlalchemy import UUID
import uuid
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(nullable=False, unique=True) #nullable = NOTNULL
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False, default='CUSTOMER')
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) #timestamp = NOW
    #mapped = base type
    #mapped_column = specific info about the column



    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.email!r}"

    # __repr__ makes the object human-readable when printed in the terminal.
    # Without it, Python would show a useless memory address like:
    # <app.models.product_variants.ProductVariant object at 0x10f3a2b50>
    # With it, you see the actual data — very useful for debugging.
    # -> str is a return type hint: it tells Python (and the developer) that this function returns a string.