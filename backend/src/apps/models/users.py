from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database.database import Base


class UsersOrm(Base):
    __tablename__ = "users"

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))

    photo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    roles: Mapped[str] = mapped_column(String(200))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    other_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
