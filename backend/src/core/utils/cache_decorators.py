from __future__ import annotations

import functools
import inspect
import hashlib
from typing import Any, Callable, Optional, Union
from datetime import timedelta

from src.apps.services.cache_service import CacheService, CacheKeyManager


def cacheable(
    cache_service: CacheService,
    key_prefix: str,
    expire: Optional[timedelta] = None,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Декоратор для кэширования результатов функций

    Args:
        cache_service: Сервис кэширования
        key_prefix: Префикс ключа кэша
        expire: Время жизни кэша
        key_builder: Функция для построения ключа из аргументов
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Строим ключ кэша
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = _build_default_key(key_prefix, func, args, kwargs)

            # Пытаемся получить из кэша
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Выполняем функцию
            result = await func(*args, **kwargs)

            # Сохраняем в кэш
            await cache_service.set(cache_key, result, expire)

            return result

        return wrapper

    return decorator


def cache_invalidate(
    cache_service: CacheService,
    patterns: Union[str, list[str]],
):
    """
    Декоратор для инвалидации кэша после выполнения функции

    Args:
        cache_service: Сервис кэширования
        patterns: Паттерны ключей для инвалидации
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Выполняем функцию
            result = await func(*args, **kwargs)

            # Инвалидируем кэш
            if isinstance(patterns, str):
                await cache_service.delete_pattern(patterns)
            else:
                for pattern in patterns:
                    await cache_service.delete_pattern(pattern)

            return result

        return wrapper

    return decorator


def _build_default_key(prefix: str, func: Callable, args: tuple, kwargs: dict) -> str:
    """Построение ключа кэша по умолчанию"""
    # Получаем параметры функции
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    # Сортируем kwargs для консистентности
    sorted_args = dict(sorted(bound_args.arguments.items()))

    # Создаем строку для хеширования
    key_data = f"{func.__module__}.{func.__qualname__}:{sorted_args}"
    hash_key = hashlib.md5(key_data.encode()).hexdigest()

    return f"{prefix}:{hash_key}"


# Специфичные декораторы для пользователей
def cache_users_list(cache_service: CacheService):
    """Декоратор для кэширования списков пользователей"""
    return cacheable(
        cache_service=cache_service,
        key_prefix="users:list",
        expire=timedelta(minutes=15),
        key_builder=lambda limit=None, offset=None: CacheKeyManager.users_list(
            limit, offset
        ),
    )


def cache_user_by_id(cache_service: CacheService):
    """Декоратор для кэширования пользователя по ID"""
    return cacheable(
        cache_service=cache_service,
        key_prefix="user:id",
        expire=timedelta(hours=1),
        key_builder=lambda user_id: CacheKeyManager.user_by_id(str(user_id)),
    )


def invalidate_users_cache(cache_service: CacheService):
    """Декоратор для инвалидации кэша пользователей"""
    return cache_invalidate(
        cache_service=cache_service,
        patterns=["users:list:*", "user:id:*", "user:phone:*", "user:email:*"],
    )
