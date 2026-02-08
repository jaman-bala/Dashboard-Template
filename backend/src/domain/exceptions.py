"""Доменные исключения - независимые от транспортного слоя"""


class DomainException(Exception):
    """Базовое доменное исключение"""

    def __init__(self, message: str, *args, **kwargs):
        self.message = message
        super().__init__(message, *args, **kwargs)


class UserDomainException(DomainException):
    """Исключения связанные с пользователями"""

    pass


class UserNotFoundException(UserDomainException):
    def __init__(self):
        super().__init__("Пользователь не найден")


class UserAlreadyExistsException(UserDomainException):
    def __init__(self):
        super().__init__("Пользователь уже существует")


class EmailAlreadyExistsException(UserDomainException):
    def __init__(self):
        super().__init__("Пользователь с таким email уже существует")


class PhoneAlreadyExistsException(UserDomainException):
    def __init__(self):
        super().__init__("Пользователь с таким номером телефона уже существует")


class IncorrectPasswordException(UserDomainException):
    def __init__(self):
        super().__init__("Неверный пароль")


class AuthenticationException(DomainException):
    """Исключения аутентификации"""

    pass


class InvalidTokenException(AuthenticationException):
    def __init__(self):
        super().__init__("Неверный токен")


class TokenValidationException(AuthenticationException):
    def __init__(self):
        super().__init__("Ошибка валидации токена")


class ExpiredTokenException(AuthenticationException):
    def __init__(self):
        super().__init__("Срок действия токена истек")


class DataValidationException(DomainException):
    """Исключения валидации данных"""

    def __init__(self, message: str = "Ошибка валидации данных"):
        super().__init__(message)


class EmailInvalidException(DataValidationException):
    def __init__(self):
        super().__init__("Некорректный формат email")


class DatabaseException(DomainException):
    """Исключения базы данных"""

    pass


class ObjectNotFoundException(DatabaseException):
    def __init__(self):
        super().__init__("Объект не найден")


class SeveralObjectsFoundException(DatabaseException):
    def __init__(self):
        super().__init__("Найдено несколько объектов")


class DatabaseConnectionException(DatabaseException):
    def __init__(self):
        super().__init__("Ошибка подключения к базе данных")


class AuthorizationException(DomainException):
    """Исключения авторизации"""

    pass


class InsufficientPermissionsException(AuthorizationException):
    def __init__(self):
        super().__init__("Недостаточно прав для выполнения действия")


class RateLimitExceededException(DomainException):
    def __init__(self):
        super().__init__("Превышен лимит запросов")


class TokenCreationException(DomainException):
    """Исключения создания токена"""

    def __init__(self, message: str = "Ошибка создания токена"):
        super().__init__(message)


class CacheOperationException(DomainException):
    """Исключения работы с кешем"""

    def __init__(self, message: str = "Ошибка операции с кешем"):
        super().__init__(message)


class SecurityValidationException(DomainException):
    """Исключения валидации безопасности"""

    def __init__(self, message: str = "Ошибка валидации безопасности"):
        super().__init__(message)


class DatabaseOperationException(DatabaseException):
    """Исключения операций с базой данных"""

    def __init__(self, message: str = "Ошибка операции с базой данных"):
        super().__init__(message)


class DatabaseIntegrityException(DatabaseException):
    def __init__(self):
        super().__init__("Нарушение целостности базы данных")


class DatabaseTransactionException(DatabaseException):
    """Исключения транзакций базы данных"""

    def __init__(self, message: str = "Ошибка транзакции базы данных"):
        super().__init__(message)
