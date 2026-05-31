from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import func
from datetime import datetime
from sqlalchemy.sql.sqltypes import UUID
import uuid
from app.models.base import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


    def __repr__(self) -> str:
        return (f"User(id={self.id!r}, name={self.email!r}, password_hash{self.password_hash!r},"
                f" created_at{self.created_at!r}")
