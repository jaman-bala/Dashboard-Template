import uuid
from datetime import datetime
from typing import Type

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from src.apps.repositories.base import BaseRepository
from src.apps.models.users import UsersOrm
from src.apps.repositories.mappers.mappers import UserDataMapper
from src.apps.dto.users import UserBaseDTO, UserWithHashedPassword
from src.core.exeptions import UserNotFoundException
from src.core.exeptions import SeveralObjectsFoundException


class UsersRepository(BaseRepository[UsersOrm, UserBaseDTO]):
    """Репозиторий пользователей."""

    model: Type[UsersOrm] = UsersOrm
    mapper = UserDataMapper

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    # ---------- READ ----------

    async def get_users(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[UserBaseDTO]:
        return await self.get_filtered(limit=limit, offset=offset)

    async def get_by_email(
        self,
        email: EmailStr,
    ) -> UserWithHashedPassword | None:
        stmt = select(self.model).filter_by(email=email)
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()

        if model is None:
            return None

        return UserWithHashedPassword.model_validate(model)

    async def get_by_phone(
        self,
        phone: str,
    ) -> UserWithHashedPassword | None:
        stmt = select(self.model).filter_by(phone=phone)
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()

        if model is None:
            return None

        return UserWithHashedPassword.model_validate(model)

    # ---------- WRITE ----------

    async def update_hashed_password(
        self,
        user_id: uuid.UUID,
        hashed_password: str,
    ) -> None:
        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(hashed_password=hashed_password)
            .returning(self.model.id)
        )

        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            raise UserNotFoundException

        if len(rows) > 1:
            raise SeveralObjectsFoundException

    async def update_last_login(
        self,
        user_id: uuid.UUID,
        last_login: datetime,
    ) -> None:
        # Получаем текущие other_data
        user = await self.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundException

        # Обновляем other_data с добавлением last_login
        current_other_data = user.other_data or {}
        current_other_data["last_login"] = last_login.isoformat()

        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(other_data=current_other_data)
            .returning(self.model.id)
        )

        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            raise UserNotFoundException

        if len(rows) > 1:
            raise SeveralObjectsFoundException

    async def update_other_data(
        self,
        user_id: uuid.UUID,
        other_data: dict,
    ) -> None:
        stmt = (
            update(self.model)
            .where(self.model.id == user_id)
            .values(other_data=other_data)
            .returning(self.model.id)
        )

        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            raise UserNotFoundException

        if len(rows) > 1:
            raise SeveralObjectsFoundException
