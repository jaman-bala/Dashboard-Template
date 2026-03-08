from __future__ import annotations

import uuid
from datetime import datetime, timedelta
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
from src.core.utils.cache_decorators import (
    cache_users_list,
)
from src.apps.services.cache_service import CacheService
from src.core.pagination import PaginationParams


class UsersRepository(BaseRepository[UsersOrm, UserBaseDTO]):
    """Репозиторий пользователей."""

    model: Type[UsersOrm] = UsersOrm
    mapper = UserDataMapper

    def __init__(
        self, session: AsyncSession, cache_service: CacheService | None = None
    ) -> None:
        super().__init__(session)
        self._cache_service = cache_service

    # ---------- READ ----------

    async def get_users(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[UserBaseDTO]:
        if self._cache_service:
            # Используем декоратор через вызов метода
            return await self._get_users_cached(limit=limit, offset=offset)
        return await self.get_filtered(limit=limit, offset=offset)

    async def get_users_paginated(
        self,
        pagination: PaginationParams,
    ) -> tuple[list[UserBaseDTO], int]:
        """Получение пользователей с пагинацией"""
        if self._cache_service:
            # Кэшируем пагинированные результаты
            return await self._get_users_paginated_cached(pagination)

        # Без кэша - прямой запрос
        users = await self.get_filtered(limit=pagination.size, offset=pagination.offset)
        total = await self.get_count()
        return users, total

    async def get_count(self) -> int:
        """Получение общего количества пользователей"""
        from sqlalchemy import func, select

        stmt = select(func.count(self.model.id))
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def _get_users_paginated_cached(
        self,
        pagination: PaginationParams,
    ) -> tuple[list[UserBaseDTO], int]:
        """Кэшированная версия получения пользователей с пагинацией"""

        # Создаем ключ кэша для пагинации
        cache_key = f"users:list:page={pagination.page}&size={pagination.size}"

        # Проверяем кэш
        cached_data = await self._cache_service.get(cache_key)
        if cached_data:
            # Восстанавливаем из кэша
            users = [UserBaseDTO.model_validate(user) for user in cached_data["users"]]
            total = cached_data["total"]
            return users, total

        # Если нет в кэше, получаем из БД
        users = await self.get_filtered(limit=pagination.size, offset=pagination.offset)
        total = await self.get_count()

        # Сохраняем в кэш на 15 минут
        cache_data = {"users": [user.model_dump() for user in users], "total": total}
        await self._cache_service.set(cache_key, cache_data, timedelta(minutes=15))

        return users, total

    async def _get_users_cached(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[UserBaseDTO]:
        """Кэшированная версия получения пользователей"""

        # Создаем декоратор динамически
        decorator = cache_users_list(self._cache_service)

        @decorator
        async def get_filtered_cached(
            limit: int | None = None, offset: int | None = None
        ):
            return await self.get_filtered(limit=limit, offset=offset)

        return await get_filtered_cached(limit=limit, offset=offset)

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

        # Инвалидируем кэш
        if self._cache_service:
            await self._cache_service.delete_pattern("users:list:*")
            await self._cache_service.delete(f"user:id:{user_id}")

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

        # Инвалидируем кэш
        if self._cache_service:
            await self._cache_service.delete_pattern("users:list:*")
            await self._cache_service.delete(f"user:id:{user_id}")
