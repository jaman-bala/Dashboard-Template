from __future__ import annotations

from sqlalchemy import Boolean, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from src.core.database.database import Base
from src.apps.models.role import Role


class UsersOrm(Base):
    __tablename__ = "users"

    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    email: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))

    photo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    roles: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    other_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
