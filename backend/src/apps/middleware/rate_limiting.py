import logging
from typing import Dict, Tuple, Optional
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.core.init import redis_manager
from src.core.config import settings

logger = logging.getLogger(__name__)

# Создаем лимитер с Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    enabled=settings.MODE != "TEST",  # Отключаем в тестах
)

# Настройки rate limiting
RATE_LIMITS = {
    "auth": {
        "login": "5/minute",  # 5 попыток входа в минуту
        "register": "3/minute",  # 3 регистрации в минуту
        "password_reset": "3/hour",  # 3 сброса пароля в час
        "refresh": "10/minute",  # 10 обновлений токена в минуту
    },
    "api": {
        "general": "100/minute",  # 100 запросов в минуту
        "upload": "10/minute",  # 10 загрузок в минуту
        "admin": "200/minute",  # 200 запросов для админов
        "search": "30/minute",  # 30 поисков в минуту
    },
    "static": {
        "avatars": "20/minute",  # 20 запросов к аватарам
        "files": "15/minute",  # 15 запросов к файлам
    },
}


class RateLimitMiddleware:
    """Улучшенный middleware для rate limiting с поддержкой разных стратегий"""

    def __init__(self, app):
        self.app = app
        self._endpoint_cache: Dict[str, str] = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Пропускаем health checks и metrics
            if self._is_excluded_endpoint(request.url.path):
                await self.app(scope, receive, send)
                return

            # Применяем rate limiting
            try:
                await self._check_rate_limit(request)
            except RateLimitExceeded as e:
                await self._handle_rate_limit_exceeded(scope, receive, send, e)
                return
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                # В случае ошибки пропускаем запрос

        await self.app(scope, receive, send)

    async def _check_rate_limit(self, request: Request) -> None:
        """Проверка rate limit для конкретного запроса"""
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path

        # Определяем лимит для endpoint с кешированием
        limit = self._get_limit_for_endpoint_cached(endpoint)
        if not limit:
            return

        # Проверяем лимит через Redis
        key = f"rate_limit:{client_ip}:{endpoint}"

        try:
            max_requests, time_window = self._parse_limit(limit)

            # Используем Redis incr для атомарности
            current_count = await redis_manager.incr(key)

            # Устанавливаем expiry только для первого запроса
            if current_count == 1:
                await redis_manager.expire(key, int(time_window))

            # Проверяем превышение лимита
            if current_count > max_requests:
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {max_requests}/{limit.split('/')[1]}"
                )

        except Exception as redis_error:
            logger.warning(
                f"Redis connection failed, skipping rate limit check: {redis_error}"
            )
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            raise

    def _get_limit_for_endpoint_cached(self, endpoint: str) -> Optional[str]:
        """Определяет лимит для endpoint с кешированием"""
        if endpoint in self._endpoint_cache:
            return self._endpoint_cache[endpoint]

        limit = self._get_limit_for_endpoint(endpoint)
        self._endpoint_cache[endpoint] = limit
        return limit

    def _get_limit_for_endpoint(self, endpoint: str) -> Optional[str]:
        """Определяет лимит для конкретного endpoint"""
        # Auth endpoints
        if "/auth/login" in endpoint:
            return RATE_LIMITS["auth"]["login"]
        elif "/auth/register" in endpoint or "/auth/create" in endpoint:
            return RATE_LIMITS["auth"]["register"]
        elif "/auth/change_password" in endpoint:
            return RATE_LIMITS["auth"]["password_reset"]
        elif "/auth/refresh" in endpoint:
            return RATE_LIMITS["auth"]["refresh"]

        # Static endpoints
        elif "/static/avatars" in endpoint:
            return RATE_LIMITS["static"]["avatars"]
        elif "/static/files" in endpoint or "/static/upload" in endpoint:
            return RATE_LIMITS["static"]["files"]

        # API endpoints
        elif "/admin" in endpoint:
            return RATE_LIMITS["api"]["admin"]
        elif "/search" in endpoint:
            return RATE_LIMITS["api"]["search"]
        elif "/upload" in endpoint:
            return RATE_LIMITS["api"]["upload"]
        else:
            return RATE_LIMITS["api"]["general"]

    def _parse_limit(self, limit_str: str) -> Tuple[int, int]:
        """Парсит строку лимита (например, '5/minute') в (count, seconds)"""
        try:
            count, period = limit_str.split("/")
            count = int(count)

            period_multipliers = {
                "second": 1,
                "minute": 60,
                "hour": 3600,
                "day": 86400,
                "month": 2592000,
            }

            seconds = period_multipliers.get(period.lower(), 60)
            return count, seconds
        except (ValueError, AttributeError) as e:
            logger.error(f"Invalid limit format: {limit_str}, error: {e}")
            return 100, 60  # Default fallback

    def _get_client_ip(self, request: Request) -> str:
        """Получает IP адрес клиента с учетом прокси"""
        # Проверяем заголовки от прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        return get_remote_address(request)

    def _is_excluded_endpoint(self, path: str) -> bool:
        """Исключенные endpoints из rate limiting"""
        excluded_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]
        return any(path.startswith(excluded) for excluded in excluded_paths)

    async def _handle_rate_limit_exceeded(
        self, scope, receive, send, error: RateLimitExceeded
    ):
        """Обработка превышения rate limit"""
        import json

        retry_after = getattr(error, "retry_after", 60)

        response_data = {
            "error": "RateLimitExceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": retry_after,
            "limit_info": {"max_requests": "N/A", "window": "N/A"},
        }

        # Логируем превышение лимита
        logger.warning(
            f"Rate limit exceeded: {error}. Retry after: {retry_after} seconds"
        )

        # Отправляем ответ
        response = {
            "type": "http.response.start",
            "status": 429,
            "headers": [
                [b"content-type", b"application/json"],
                [b"retry-after", str(retry_after).encode()],
            ],
        }

        await send(response)

        body = json.dumps(response_data).encode()
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )


# Декораторы для rate limiting
def rate_limit(limit: str):
    """Декоратор для применения rate limiting к endpoint"""

    def decorator(func):
        return limiter.limit(limit)(func)

    return decorator


# Готовые декораторы для разных типов запросов
login_rate_limit = rate_limit(RATE_LIMITS["auth"]["login"])
register_rate_limit = rate_limit(RATE_LIMITS["auth"]["register"])
password_reset_rate_limit = rate_limit(RATE_LIMITS["auth"]["password_reset"])
refresh_rate_limit = rate_limit(RATE_LIMITS["auth"]["refresh"])
upload_rate_limit = rate_limit(RATE_LIMITS["api"]["upload"])
admin_rate_limit = rate_limit(RATE_LIMITS["api"]["admin"])
search_rate_limit = rate_limit(RATE_LIMITS["api"]["search"])
general_rate_limit = rate_limit(RATE_LIMITS["api"]["general"])


# Middleware для добавления в FastAPI app
def setup_rate_limiting(app):
    """Настраивает rate limiting для FastAPI приложения"""
    app.add_middleware(RateLimitMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
