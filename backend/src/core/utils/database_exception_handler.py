import logging

from sqlalchemy.exc import (
    IntegrityError,
    OperationalError,
    DatabaseError,
    SQLAlchemyError,
    DisconnectionError,
    TimeoutError as SQLTimeoutError,
)

from src.core.exeptions import (
    DatabaseIntegrityException,
    DatabaseConnectionException,
    DatabaseOperationException,
)

logger = logging.getLogger(__name__)


class DatabaseExceptionHandler:
    """Обработчик исключений базы данных."""

    # Маппинг SQLAlchemy исключений на наши собственные
    EXCEPTION_MAPPING = {
        IntegrityError: DatabaseIntegrityException,
        OperationalError: DatabaseConnectionException,
        DisconnectionError: DatabaseConnectionException,
        SQLTimeoutError: DatabaseConnectionException,
        DatabaseError: DatabaseOperationException,
        SQLAlchemyError: DatabaseOperationException,
    }

    @classmethod
    def handle_database_exception(
        cls, exception: Exception, context: str = ""
    ) -> Exception:
        """
        Обрабатывает исключение базы данных и преобразует в соответствующее исключение сервисного слоя.

        Args:
            exception: Исключение от SQLAlchemy
            context: Контекст операции (например, "user registration", "user update")

        Returns:
            Соответствующее исключение сервисного слоя
        """
        exception_type = type(exception)

        # Логируем исходное исключение
        logger.error(
            f"Database exception in {context}: {exception_type.__name__}: {str(exception)}"
        )

        # Проверяем, есть ли маппинг для этого типа исключения
        if exception_type in cls.EXCEPTION_MAPPING:
            mapped_exception_class = cls.EXCEPTION_MAPPING[exception_type]

            # Создаем сообщение с контекстом
            message = f"Database error during {context}: {str(exception)}"

            # Возвращаем соответствующее исключение
            return mapped_exception_class(message)

        # Если маппинг не найден, возвращаем общее исключение БД
        message = f"Unexpected database error during {context}: {str(exception)}"
        return DatabaseOperationException(message)

    @classmethod
    def handle_integrity_error(
        cls, exception: IntegrityError, context: str = ""
    ) -> Exception:
        """
        Специальная обработка IntegrityError для определения типа нарушения.

        Args:
            exception: IntegrityError от SQLAlchemy
            context: Контекст операции

        Returns:
            Соответствующее исключение сервисного слоя
        """
        error_message = (
            str(exception.orig) if hasattr(exception, "orig") else str(exception)
        )

        # Анализируем сообщение об ошибке для определения типа нарушения
        if "unique" in error_message.lower():
            if "email" in error_message.lower():
                from src.core.exeptions import UserAlreadyExistsException

                return UserAlreadyExistsException("User with this email already exists")
            elif "phone" in error_message.lower():
                from src.core.exeptions import PhoneAlreadyExistsException

                return PhoneAlreadyExistsException(
                    "User with this phone already exists"
                )
            else:
                return DatabaseIntegrityException(
                    f"Unique constraint violation during {context}"
                )

        elif "foreign key" in error_message.lower():
            return DatabaseIntegrityException(
                f"Foreign key constraint violation during {context}"
            )

        elif "check constraint" in error_message.lower():
            return DatabaseIntegrityException(
                f"Check constraint violation during {context}"
            )

        else:
            return DatabaseIntegrityException(
                f"Integrity constraint violation during {context}: {error_message}"
            )

    @classmethod
    def handle_connection_error(
        cls, exception: Exception, context: str = ""
    ) -> Exception:
        """
        Специальная обработка ошибок подключения.

        Args:
            exception: Исключение подключения
            context: Контекст операции

        Returns:
            DatabaseConnectionException с соответствующим сообщением
        """
        error_message = str(exception)

        if "timeout" in error_message.lower():
            return DatabaseConnectionException(
                f"Database connection timeout during {context}"
            )
        elif "connection refused" in error_message.lower():
            return DatabaseConnectionException(
                f"Database connection refused during {context}"
            )
        elif "network" in error_message.lower():
            return DatabaseConnectionException(
                f"Network error during database operation: {context}"
            )
        else:
            return DatabaseConnectionException(
                f"Database connection error during {context}: {error_message}"
            )


# Декоратор для автоматической обработки БД исключений
def handle_database_exceptions(context: str = ""):
    """
    Декоратор для автоматической обработки исключений базы данных.

    Args:
        context: Контекст операции для логирования
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (
                IntegrityError,
                OperationalError,
                DatabaseError,
                SQLAlchemyError,
            ) as e:
                # Обрабатываем БД исключения
                handled_exception = DatabaseExceptionHandler.handle_database_exception(
                    e, context
                )
                raise handled_exception
            except Exception as e:
                # Остальные исключения пробрасываем как есть
                raise e

        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (
                IntegrityError,
                OperationalError,
                DatabaseError,
                SQLAlchemyError,
            ) as e:
                # Обрабатываем БД исключения
                handled_exception = DatabaseExceptionHandler.handle_database_exception(
                    e, context
                )
                raise handled_exception
            except Exception as e:
                # Остальные исключения пробрасываем как есть
                raise e

        # Возвращаем соответствующий wrapper в зависимости от типа функции
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
