import uuid
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from src.apps.models.role import Role
from src.core.types import PhoneNumber, PasswordStr, NonEmptyString, EmailField


class UserBaseDTO(BaseModel):
    id: uuid.UUID
    first_name: NonEmptyString | None = None
    last_name: NonEmptyString | None = None
    middle_name: NonEmptyString | None = None

    email: EmailField | None = None
    phone: PhoneNumber

    photo: str | None = None
    roles: Role
    is_active: bool
    other_data: dict[str, Any] | None = None

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,
    )


class UserRequestAddDTO(BaseModel):
    """DTO для добавления пользователя"""

    first_name: NonEmptyString | None = Field(None, description="Имя пользователя")
    last_name: NonEmptyString | None = Field(None, description="Фамилия пользователя")
    middle_name: NonEmptyString | None = Field(
        None, description="Отчество пользователя"
    )
    email: EmailField | None = Field(None, description="Email пользователя")
    phone: PhoneNumber = Field(..., description="Телефон пользователя")
    password: PasswordStr = Field(..., description="Пароль пользователя")
    photo: str | None = Field(None, description="Фото пользователя")
    roles: str = Field(default=Role.USER, description="Роль пользователя")


class UserUpdateRequestDTO(BaseModel):
    """DTO для обновления пользователя"""

    first_name: NonEmptyString | None = Field(None, description="Имя пользователя")
    last_name: NonEmptyString | None = Field(None, description="Фамилия пользователя")
    middle_name: NonEmptyString | None = Field(
        None, description="Отчество пользователя"
    )
    email: EmailField | None = Field(None, description="Email пользователя")
    phone: PhoneNumber | None = None
    photo: str | None = None
    roles: Role | None = Field(None, description="Роли пользователя")


class UserAddDTO(BaseModel):
    """DTO для добавления пользователя в базу данных."""

    id: uuid.UUID
    first_name: NonEmptyString | None = Field(None, description="Имя пользователя")
    last_name: NonEmptyString | None = Field(None, description="Фамилия пользователя")
    middle_name: NonEmptyString | None = Field(
        None, description="Отчество пользователя"
    )
    email: EmailField | None = Field(None, description="Email пользователя")
    phone: PhoneNumber
    hashed_password: str = Field(min_length=1, max_length=200)
    photo: str | None = None
    roles: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class UserResponseDTO(BaseModel):
    """DTO для ответа API с данными пользователя"""
    id: uuid.UUID
    first_name: NonEmptyString | None = None
    last_name: NonEmptyString | None = None
    middle_name: NonEmptyString | None = None
    email: EmailField | None = None
    phone: PhoneNumber
    photo: str | None = None
    roles: str
    is_active: bool
    last_login_iso: str | None = None
    exit_login_iso: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserLogoutResponseDTO(UserBaseDTO):
    message: str


class UserRequestLoginDTO(BaseModel):
    phone: PhoneNumber
    password: PasswordStr


class UserWithHashedPassword(UserBaseDTO):
    hashed_password: str = Field(min_length=1, max_length=200)


class UserRequestUpdatePasswordDTO(BaseModel):
    new_password: PasswordStr
    change_password: PasswordStr | None = None


class RefreshTokenRequestDTO(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=500)

class TokenResponseDTO(BaseModel):
    access_token: str
    last_login: str
