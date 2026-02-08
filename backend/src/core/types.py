"""Кастомные типы для валидации"""

from typing import Annotated, Optional
from pydantic import StringConstraints, AfterValidator, Field, EmailStr
from src.core.config import settings
import re


def validate_phone_logic(v: str) -> str:
    """Валидация и нормализация телефона"""
    if not v:
        raise ValueError("Phone number is required")

    v = v.strip()

    # Проверяем через regex из настроек
    if not re.match(settings.PHONE_REGEX_PATTERN, v):
        raise ValueError("Invalid phone number format")

    return v


def validate_password_strength(v: str) -> str:
    """Валидация сложности пароля"""
    if not v:
        raise ValueError("Password is required")

    # Проверяем длину
    if not (8 <= len(v) <= 72):
        raise ValueError("Password length must be between 8 and 72 characters")

    # Проверяем наличие заглавных, строчных букв и цифр программно
    has_upper = any(c.isupper() for c in v)
    has_lower = any(c.islower() for c in v)
    has_digit = any(c.isdigit() for c in v)

    if not (has_upper and has_lower and has_digit):
        raise ValueError(
            "Password must contain at least one uppercase letter, one lowercase letter, and one number"
        )

    # Проверяем базовый паттерн
    if not re.match(settings.PASSWORD_REGEX_PATTERN, v):
        raise ValueError("Password contains invalid characters")

    return v


def validate_non_empty_string(v: Optional[str]) -> Optional[str]:
    """Валидация непустых строк"""
    if v is not None:
        v = v.strip()
        if v == "":
            raise ValueError("Field cannot be an empty string")
    return v


# Переиспользуемые типы
PhoneNumber = Annotated[
    str,
    StringConstraints(
        min_length=1, max_length=20, pattern=settings.PHONE_REGEX_PATTERN
    ),
    AfterValidator(validate_phone_logic),
    Field(json_schema_extra={"example": "+996500500500"}),
]

PasswordStr = Annotated[
    str,
    StringConstraints(min_length=8, max_length=72),
    AfterValidator(validate_password_strength),
    Field(json_schema_extra={"example": "PasSw0rd123"}),
]

NonEmptyString = Annotated[
    Optional[str],
    StringConstraints(max_length=100),
    AfterValidator(validate_non_empty_string),
]

EmailField = Annotated[
    Optional[EmailStr],
    Field(None, max_length=100, json_schema_extra={"example": "user@example.com"}),
]
