from typing import Generic, Sequence, Any, Type
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.repositories.mappers.base import DataMapper
from src.apps.repositories.mappers.types import TModel, TDTO
from src.core.exeptions import ObjectNotFoundException, SeveralObjectsFoundException


class BaseRepository(Generic[TModel, TDTO]):
    """
    Базовый репозиторий.
    Работает только с ORM и domain DTO.
    Не содержит логики транспорта (HTTP).
    """

    model: Type[TModel]
    mapper: DataMapper

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---------- READ ----------

    async def get_filtered(
        self,
        *filters: Any,
        limit: int | None = None,
        offset: int | None = None,
        **filter_by: Any,
    ) -> list[TDTO]:
        stmt = select(self.model).filter(*filters).filter_by(**filter_by)

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self) -> list[TDTO]:
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by: Any) -> TDTO | None:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        model = result.scalars().one_or_none()

        if model is None:
            return None

        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by: Any) -> TDTO:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        if not models:
            raise ObjectNotFoundException

        if len(models) > 1:
            raise SeveralObjectsFoundException

        return self.mapper.map_to_domain_entity(models[0])

    # ---------- CREATE ----------

    async def add(self, data: TDTO) -> TDTO:
        payload = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        stmt = insert(self.model).values(**payload).returning(self.model)

        result = await self.session.execute(stmt)
        model = result.scalars().one()

        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: Sequence[TDTO]) -> None:
        if not data:
            return

        payload = [
            item.model_dump(exclude_unset=True, exclude_none=True) for item in data
        ]

        stmt = insert(self.model).values(payload)
        await self.session.execute(stmt)

    # ---------- UPDATE ----------

    async def _update(
        self,
        payload: dict[str, Any],
        **filter_by: Any,
    ) -> None:
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**payload)
            .returning(self.model)
        )

        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            raise ObjectNotFoundException

        if len(rows) > 1:
            raise SeveralObjectsFoundException

    async def update(self, data: TDTO, **filter_by: Any) -> None:
        payload = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        await self._update(payload, **filter_by)

    # ---------- DELETE ----------

    async def delete(self, **filter_by: Any) -> None:
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model)

        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            raise ObjectNotFoundException

        if len(rows) > 1:
            raise SeveralObjectsFoundException
