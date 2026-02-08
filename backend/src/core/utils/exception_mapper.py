import logging
from typing import Type, Dict, Any
from sqlalchemy.exc import CompileError, IntegrityError, OperationalError
from fastapi import HTTPException

from src.core.exeptions import (
    # Сервисные исключения (независимые от FastAPI)
    TokenValidationException,
    TokenCreationException,
    RateLimitExceededException,
    SecurityValidationException,
    DatabaseOperationException,
    DatabaseIntegrityException,
    DatabaseConnectionException,
    DatabaseTransactionException,
    DataValidationException,
    CacheOperationException,
    # Бизнес исключения
    UserNotFoundException,
    UserAlreadyExistsException,
    PhoneAlreadyExistsException,
    ExpiredTokenException,
    InvalidTokenException,
    ObjectNotFoundException,
    IncorrectPasswordException,
    EmailInvalidException,
)
from src.domain.exceptions import EmailAlreadyExistsException

logger = logging.getLogger(__name__)


class ExceptionMapper:
    """Маппер для преобразования исключений сервисного слоя в HTTP исключения."""

    # Маппинг исключений на HTTP статус коды и сообщения
    EXCEPTION_MAPPING: Dict[Type[Exception], Dict[str, Any]] = {
        # Токены и аутентификация
        TokenValidationException: {
            "status_code": 401,
            "detail": "Token validation failed",
        },
        TokenCreationException: {"status_code": 500, "detail": "Token creation failed"},
        ExpiredTokenException: {"status_code": 401, "detail": "Token has expired"},
        InvalidTokenException: {"status_code": 401, "detail": "Invalid token"},
        # Пользователи
        UserNotFoundException: {"status_code": 404, "detail": "User not found"},
        UserAlreadyExistsException: {
            "status_code": 409,
            "detail": "User already exists",
        },
        PhoneAlreadyExistsException: {
            "status_code": 409,
            "detail": "Пользователь с таким номером телефона уже существует",
        },
        EmailAlreadyExistsException: {
            "status_code": 409,
            "detail": "Пользователь с таким email уже существует",
        },
        IncorrectPasswordException: {
            "status_code": 401,
            "detail": "Incorrect password",
        },
        # Безопасность
        SecurityValidationException: {
            "status_code": 400,
            "detail": "Security validation failed",
        },
        RateLimitExceededException: {
            "status_code": 429,
            "detail": "Rate limit exceeded",
        },
        # Системные ошибки
        DatabaseOperationException: {
            "status_code": 500,
            "detail": "Database operation failed",
        },
        DatabaseIntegrityException: {
            "status_code": 409,
            "detail": "Database integrity violation",
        },
        DatabaseConnectionException: {
            "status_code": 503,
            "detail": "Database connection failed",
        },
        DatabaseTransactionException: {
            "status_code": 500,
            "detail": "Database transaction failed",
        },
        DataValidationException: {
            "status_code": 400,
            "detail": "Data validation failed",
        },
        CacheOperationException: {
            "status_code": 500,
            "detail": "Cache operation failed",
        },
        ObjectNotFoundException: {"status_code": 404, "detail": "Object not found"},
        EmailInvalidException: {"status_code": 400, "detail": "Invalid email format"},
        # Pydantic validation errors
        ValueError: {"status_code": 400, "detail": "Validation error"},
        TypeError: {"status_code": 400, "detail": "Type error: invalid argument types"},
        # SQLAlchemy ошибки
        CompileError: {
            "status_code": 500,
            "detail": "Database query compilation error",
        },
        IntegrityError: {"status_code": 409, "detail": "Database integrity violation"},
        OperationalError: {"status_code": 500, "detail": "Database operational error"},
    }

    @classmethod
    def map_to_http_exception(cls, exception: Exception) -> HTTPException:
        """Преобразует исключение сервисного слоя в HTTP исключение."""
        exception_type = type(exception)

        # Проверяем, есть ли маппинг для этого типа исключения
        if exception_type in cls.EXCEPTION_MAPPING:
            mapping = cls.EXCEPTION_MAPPING[exception_type]
            status_code = mapping["status_code"]
            detail = mapping["detail"]

            # Используем сообщение из исключения если оно есть
            if hasattr(exception, "detail") and exception.detail:
                detail = exception.detail
            elif hasattr(exception, "args") and exception.args:
                detail = str(exception.args[0])

            logger.warning(
                f"Mapping {exception_type.__name__} to HTTP {status_code}: {detail}"
            )
            return HTTPException(status_code=status_code, detail=detail)

        # Если маппинг не найден, возвращаем общую ошибку
        logger.error(f"No mapping found for exception: {exception_type.__name__}")
        return HTTPException(
            status_code=500, detail=f"Internal server error: {exception_type.__name__}"
        )

    @classmethod
    def handle_service_exception(cls, exception: Exception) -> HTTPException:
        """Обрабатывает исключение сервисного слоя и возвращает HTTP исключение."""
        if isinstance(exception, HTTPException):
            return exception

        try:
            return cls.map_to_http_exception(exception)
        except Exception as e:
            logger.error(f"Error mapping exception: {e}")
            return HTTPException(status_code=500, detail="Internal server error")


# Декоратор для автоматического маппинга исключений
def handle_service_exceptions(func):
    """Декоратор для автоматического маппинга исключений сервисного слоя."""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Проверяем, является ли это уже HTTPException
            if isinstance(e, HTTPException):
                raise e

            # Маппим сервисные исключения в HTTP исключения
            http_exception = ExceptionMapper.handle_service_exception(e)
            raise http_exception

    return wrapper


# Синхронная версия декоратора
def handle_service_exceptions_sync(func):
    """Синхронная версия декоратора для маппинга исключений."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Проверяем, является ли это уже HTTPException
            if isinstance(e, HTTPException):
                raise e

            # Маппим сервисные исключения в HTTP исключения
            http_exception = ExceptionMapper.handle_service_exception(e)
            raise http_exception

    return wrapper
