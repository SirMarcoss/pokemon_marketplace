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

    #method for good format when printed in the terminal