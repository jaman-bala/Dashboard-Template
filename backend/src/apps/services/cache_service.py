from __future__ import annotations

import json
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic
from datetime import timedelta

from src.apps.connectors.redis_connector import RedisManager

T = TypeVar("T")


class CacheService(ABC, Generic[T]):
    """Interface для кэширования"""

    @abstractmethod
    async def get(self, key: str) -> Optional[T]:
        """Получить данные из кэша"""
        pass

    @abstractmethod
    async def set(self, key: str, value: T, expire: Optional[timedelta] = None) -> None:
        """Сохранить данные в кэш"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удалить данные из кэша"""
        pass

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> None:
        """Удалить данные по паттерну"""
        pass


class RedisCacheService(CacheService[T]):
    """Redis реализация кэш сервиса"""

    def __init__(self, redis_manager: RedisManager):
        self._redis = redis_manager

    async def get(self, key: str) -> Optional[T]:
        """Получить данные из кэша с десериализацией"""
        try:
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    async def set(self, key: str, value: T, expire: Optional[timedelta] = None) -> None:
        """Сохранить данные в кэш с сериализацией"""
        try:
            serialized_data = json.dumps(value, default=str)
            expire_seconds = int(expire.total_seconds()) if expire else None
            await self._redis.set(key, serialized_data, expire_seconds)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        """Удалить данные из кэша"""
        try:
            await self._redis.delete(key)
        except Exception:
            pass

    async def delete_pattern(self, pattern: str) -> None:
        """Удалить данные по паттерну"""
        try:
            keys = await self._redis.redis.keys(pattern)
            if keys:
                await self._redis.redis.delete(*keys)
        except Exception:
            pass


class CacheKeyManager:
    """SRP: Управление ключами кэша"""

    @staticmethod
    def users_list(limit: int | None = None, offset: int | None = None) -> str:
        """Ключ для списка пользователей"""
        params = f"limit={limit}&offset={offset}"
        return f"users:list:{hashlib.md5(params.encode()).hexdigest()}"

    @staticmethod
    def user_by_id(user_id: str) -> str:
        """Ключ для пользователя по ID"""
        return f"user:id:{user_id}"

    @staticmethod
    def user_by_phone(phone: str) -> str:
        """Ключ для пользователя по телефону"""
        return f"user:phone:{hashlib.md5(phone.encode()).hexdigest()}"

    @staticmethod
    def user_by_email(email: str) -> str:
        """Ключ для пользователя по email"""
        return f"user:email:{hashlib.md5(email.encode()).hexdigest()}"


class CacheInvalidator:
    """SRP: Инвалидация кэша при изменениях"""

    def __init__(self, cache_service: CacheService):
        self._cache = cache_service

    async def invalidate_user_cache(self, user_id: str) -> None:
        """Инвалидация всего кэша связанного с пользователем"""
        # Удаляем все списки пользователей
        await self._cache.delete_pattern("users:list:*")

        # Удаляем конкретного пользователя по ID
        await self._cache.delete(CacheKeyManager.user_by_id(user_id))

    async def invalidate_users_list_cache(self) -> None:
        """Инвалидация кэша списков пользователей"""
        await self._cache.delete_pattern("users:list:*")

    async def invalidate_user_by_phone(self, phone: str) -> None:
        """Инвалидация кэша пользователя по телефону"""
        await self._cache.delete(CacheKeyManager.user_by_phone(phone))

    async def invalidate_user_by_email(self, email: str) -> None:
        """Инвалидация кэша пользователя по email"""
        await self._cache.delete(CacheKeyManager.user_by_email(email))


# Factory для создания кэш сервиса
class CacheServiceFactory:
    """Factory для создания кэш сервиса"""

    @staticmethod
    def create_redis_cache(redis_manager: RedisManager) -> RedisCacheService[Any]:
        """Создать Redis кэш сервис"""
        return RedisCacheService(redis_manager)
