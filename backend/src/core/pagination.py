from __future__ import annotations

from typing import Generic, TypeVar, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, validator

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    page: int = Field(default=1, ge=1, description="Номер страницы")
    size: int = Field(default=20, ge=1, le=100, description="Размер страницы")

    @property
    def offset(self) -> int:
        """Вычисление offset для SQL"""
        return (self.page - 1) * self.size

    @validator("size")
    @classmethod
    def validate_size(cls, v: int) -> int:
        """Валидация максимального размера"""
        if v > 100:
            raise ValueError("Максимальный размер страницы - 100")
        return v


class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией"""

    items: list[T] = Field(description="Элементы текущей страницы")
    total: int = Field(description="Общее количество элементов")
    page: int = Field(description="Текущая страница")
    size: int = Field(description="Размер страницы")
    pages: int = Field(description="Общее количество страниц")

    @property
    def has_next(self) -> bool:
        """Есть ли следующая страница"""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Есть ли предыдущая страница"""
        return self.page > 1

    @property
    def next_page(self) -> Optional[int]:
        """Номер следующей страницы"""
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> Optional[int]:
        """Номер предыдущей страницы"""
        return self.page - 1 if self.has_prev else None

    model_config = ConfigDict(from_attributes=True)


class PaginationMetadata(BaseModel):
    """Метаданные пагинации"""

    current_page: int
    per_page: int
    total_pages: int
    total_items: int
    has_next_page: bool
    has_prev_page: bool
    next_page_number: Optional[int] = None
    prev_page_number: Optional[int] = None

    @classmethod
    def create(cls, page: int, size: int, total: int) -> PaginationMetadata:
        """Создание метаданных"""
        pages = (total + size - 1) // size if total > 0 else 0

        return cls(
            current_page=page,
            per_page=size,
            total_pages=pages,
            total_items=total,
            has_next_page=page < pages,
            has_prev_page=page > 1,
            next_page_number=page + 1 if page < pages else None,
            prev_page_number=page - 1 if page > 1 else None,
        )


def paginate_query(query, pagination: PaginationParams):
    """Применение пагинации к SQLAlchemy query"""
    return query.offset(pagination.offset).limit(pagination.size)


def create_paginated_response(
    items: list[T],
    total: int,
    pagination: PaginationParams,
    response_model: type[BaseModel],
) -> PaginatedResponse[T]:
    """Создание пагинированного ответа"""
    pages = (total + pagination.size - 1) // pagination.size if total > 0 else 0

    return PaginatedResponse[T](
        items=[response_model.model_validate(item) for item in items],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=pages,
    )
