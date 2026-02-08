from fastapi import HTTPException
from src.domain.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    PhoneAlreadyExistsException,
    InvalidTokenException,
    ExpiredTokenException,
    DataValidationException,
    EmailInvalidException,
    ObjectNotFoundException,
    SeveralObjectsFoundException,
    InsufficientPermissionsException,
    RateLimitExceededException,
    TokenCreationException,
    CacheOperationException,
    IncorrectPasswordException,
    SecurityValidationException,
    DatabaseOperationException,
    DatabaseIntegrityException,
    DatabaseTransactionException,
    DatabaseConnectionException,
    TokenValidationException,
)

# Переэкспорт доменных исключений для обратной совместимости
__all__ = [
    "UserNotFoundException",
    "UserAlreadyExistsException",
    "PhoneAlreadyExistsException",
    "InvalidTokenException",
    "ExpiredTokenException",
    "DataValidationException",
    "EmailInvalidException",
    "ObjectNotFoundException",
    "SeveralObjectsFoundException",
    "InsufficientPermissionsException",
    "RateLimitExceededException",
    "TokenCreationException",
    "CacheOperationException",
    "IncorrectPasswordException",
    "SecurityValidationException",
    "DatabaseOperationException",
    "DatabaseIntegrityException",
    "DatabaseTransactionException",
    "DatabaseConnectionException",
    "TokenValidationException",
]


class AllErrorHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserEmailAlreadyExistsHTTPException(AllErrorHTTPException):
    status_code = 409
    detail = "Пользователь с таким email не зарегистрирован"


class UserPhoneAlreadyExistsHTTPException(AllErrorHTTPException):
    status_code = 409
    detail = "Пользователь с таким номером зарегистрирован"


class UserAlreadyHTTPException(AllErrorHTTPException):
    status_code = 409
    detail = "Пользователь уже существует"


class UserEmailAlreadyHTTPException(AllErrorHTTPException):
    status_code = 409
    detail = "Пользователь с таким email зарегистрирован"


class IncorrectPasswordHTTPException(AllErrorHTTPException):
    status_code = 401
    detail = "Пароль или Логин неверный"


class IncorrectTokenHTTPException(AllErrorHTTPException):
    status_code = 401
    detail = "Неправильный токен доступа"


class InnAlreadyExistsHTTPException(AllErrorHTTPException):
    status_code = 409
    detail = "Пользователь с таким ИНН уже существует"


class UserNotRegisteredHTTPException(AllErrorHTTPException):
    status_code = 404
    detail = "Пользователь не зарегистрирован"


class ExpiredTokenHTTPException(AllErrorHTTPException):
    status_code = 401
    detail = "Срок действия токена истек"


class FaceNotImagesHTTPException(AllErrorHTTPException):
    status_code = 401
    detail = "Лицо не найдено в базе данных"


class ForbiddenHTTPException(AllErrorHTTPException):
    status_code = 403
    detail = "Недостаточно прав!"


class ImagesFormatHTTPException(AllErrorHTTPException):
    status_code = 400
    detail = "Неподдерживаемый тип файла. Допустимы только JPEG или PNG."


class ImagesSizeHTTPException(AllErrorHTTPException):
    status_code = 400
    detail = "Размер изображения превышает допустимый размер."


class ImagesAlreadyHTTPException(AllErrorHTTPException):
    status_code = 404
    detail = "Изображение не найдено"


class CurrentRolesHTTPException(AllErrorHTTPException):
    status_code = 401
    detail = "Недостаточно прав для выполнения этого действия."


class RolesSuperuserHTTPException(AllErrorHTTPException):
    status_code = 403
    detail = "Доступ запрещен. Только суперпользователь может использовать эту ручку."


class RolesAdminHTTPException(AllErrorHTTPException):
    status_code = 403
    detail = "Доступ запрещен. Только администратор может использовать эту ручку."


class RolesUserHTTPException(AllErrorHTTPException):
    status_code = 403
    detail = "Доступ запрещен. У вас нет прав."


class TicketNotFoundException(AllErrorHTTPException):
    status_code = 404
    detail = "Тикет не найден"
