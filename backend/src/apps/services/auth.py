from __future__ import annotations

import uuid
import logging
from datetime import datetime


from passlib.context import CryptContext

from src.core.utils.logging_config import log_audit_event
from src.domain.exceptions import (
    UserNotFoundException,
    IncorrectPasswordException,
    PhoneAlreadyExistsException,
    EmailAlreadyExistsException,
)
from src.apps.dto.users import (
    UserBaseDTO,
    UserAddDTO,
    UserResponseDTO,
    UserUpdateRequestDTO,
    UserRequestAddDTO,
    UserRequestLoginDTO,
    UserRequestUpdatePasswordDTO,
    TokenResponseDTO,
    GenerateTokenResponseDTO,
)
from src.apps.services.base import BaseService
from src.apps.services.token_service import TokenService
from src.core.pagination import PaginationParams, PaginatedResponse


logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """Сервис аутентификации и управления пользователями"""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

    def __init__(self, db):
        super().__init__(db)
        self._token_service = TokenService()

    # ----------------- PASSWORD OPERATIONS -----------------

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)

    # ----------------- TOKEN OPERATIONS -----------------

    async def create_access_token(self, user_id: uuid.UUID, roles: list[str]) -> str:
        """Создание access токена"""
        return await self._token_service.create_token(user_id, roles, "access")

    async def create_refresh_token(self, user_id: uuid.UUID, roles: list[str]) -> str:
        """Создание refresh токена"""
        return await self._token_service.create_token(user_id, roles, "refresh")

    async def decode_access_token(self, token: str) -> dict:
        """Декодирование access токена"""
        return await self._token_service.validate_token(token, "access")

    # ----------------- AUTHENTICATION -----------------

    async def login_user(self, data: UserRequestLoginDTO) -> TokenResponseDTO:
        """Вход пользователя"""
        user = await self._authenticate_user(data)

        # Обновляем last_login
        await self.db.users.update_last_login(user.id, datetime.utcnow())
        await self.db.commit()

        tokens = await self._generate_tokens(user)
        await self._log_audit_event(user, "login")

        return TokenResponseDTO(
            access_token=tokens.access_token,
            last_login=datetime.utcnow().isoformat(),
        )

    async def logout_user(
        self, access_token: str = None, user_id: str | uuid.UUID = None
    ) -> None:
        """Выход пользователя"""
        logger.info(
            f"Logout attempt - access_token: {bool(access_token)}, user_id: {user_id}"
        )

        await self._token_service.logout_user(access_token, user_id)

        if user_id:
            user_id_str = str(user_id) if isinstance(user_id, uuid.UUID) else user_id
            logger.info(f"Updating exit_login_time for user: {user_id_str}")
            await self._update_exit_login_time(user_id_str)
            await self._log_audit_event_simple(user_id_str, "logout")
        else:
            logger.warning("No user_id provided for logout")

    # ----------------- USER MANAGEMENT -----------------

    async def register_user(self, data: UserRequestAddDTO) -> UserAddDTO:
        existing_user_by_phone = await self.db.users.get_one_or_none(phone=data.phone)
        if existing_user_by_phone:
            raise PhoneAlreadyExistsException()

        existing_user_by_email = await self.db.users.get_one_or_none(email=data.email)
        if existing_user_by_email:
            raise EmailAlreadyExistsException()

        new_user = await self._create_user(data)
        await self.db.commit()
        await self._log_audit_event(new_user, "register")
        return new_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserResponseDTO:
        """Получение пользователя по ID"""
        user = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundException
        return self._map_user_to_response(user)

    async def get_me(self, user_id: uuid.UUID) -> UserResponseDTO:
        """Получение текущего пользователя"""
        return await self.get_user_by_id(user_id)

    async def get_all_users(
        self, pagination: PaginationParams | None = None
    ) -> PaginatedResponse[UserResponseDTO] | list[UserResponseDTO]:
        """Получение всех пользователей с пагинацией или списком"""
        if pagination:
            users, total = await self.db.users.get_users_paginated(pagination)
            if not users:
                raise UserNotFoundException

            return PaginatedResponse[UserResponseDTO](
                items=[self._map_user_to_response(user) for user in users],
                total=total,
                page=pagination.page,
                size=pagination.size,
                pages=(total + pagination.size - 1) // pagination.size
                if total > 0
                else 0,
            )
        else:
            users = await self.db.users.get_users()
            if not users:
                raise UserNotFoundException
            return [self._map_user_to_response(user) for user in users]

    async def patch_user(
        self, user_id: uuid.UUID, data: UserUpdateRequestDTO
    ) -> UserResponseDTO:
        """Обновление данных пользователя"""
        await self._ensure_user_exists(user_id)
        await self.db.users.update(data, id=user_id)
        await self.db.commit()
        return self._map_user_to_response(
            await self.db.users.get_one_or_none(id=user_id)
        )

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Удаление пользователя"""
        await self.db.users.delete(id=user_id)
        await self.db.commit()

    async def change_password(
        self, user_id: uuid.UUID, data: UserRequestUpdatePasswordDTO
    ) -> None:
        """Изменение пароля пользователя"""
        await self._ensure_user_exists(user_id)
        hashed_password = self.hash_password(data.new_password)
        await self.db.users.update_hashed_password(user_id, hashed_password)
        await self.db.commit()

    # ----------------- TOKEN OPERATIONS -----------------

    async def refresh_access_token(self, refresh_token: str) -> str:
        """Обновление access токена"""
        return await self._token_service.refresh_access_token(refresh_token, self.db)

    # ----------------- AVATAR OPERATIONS -----------------

    async def patch_avatars(
        self, user_id: uuid.UUID, avatar_url: str | None = None
    ) -> UserResponseDTO:
        """Обновление аватара пользователя"""
        await self._ensure_user_exists(user_id)

        if avatar_url:
            patch_data = UserUpdateRequestDTO(photo=avatar_url)
            await self.db.users.update(patch_data, id=user_id)
            await self.db.commit()

        return self._map_user_to_response(
            await self.db.users.get_one_or_none(id=user_id)
        )

    # ----------------- PRIVATE METHODS -----------------

    async def _authenticate_user(self, data: UserRequestLoginDTO):
        """Аутентификация пользователя"""
        user = await self.db.users.get_by_phone(data.phone)
        if not user or not user.is_active:
            raise UserNotFoundException

        if not self.verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException

        return user

    async def _generate_tokens(self, user) -> GenerateTokenResponseDTO:
        """Генерация токенов для пользователя"""
        roles_list = self._extract_roles(user.roles)
        access_token = await self.create_access_token(user.id, roles_list)
        refresh_token = await self.create_refresh_token(user.id, roles_list)
        return GenerateTokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def _ensure_user_exists(self, user_id: uuid.UUID):
        """Проверка существования пользователя"""
        user = await self.db.users.get_one_or_none(id=user_id)
        if not user:
            raise UserNotFoundException
        return user

    async def _create_user(self, user_data: dict) -> UserAddDTO:
        """Создание пользователя"""
        hashed_password = self.hash_password(user_data.password)
        new_user = UserAddDTO(
            id=uuid.uuid4(),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            middle_name=user_data.middle_name,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=hashed_password,
            photo=user_data.photo,
            roles=user_data.roles,
        )
        await self.db.users.add(new_user)
        return new_user

    async def _update_exit_login_time(self, user_id: str) -> None:
        """Обновление времени выхода"""
        user = await self.db.users.get_one_or_none(id=uuid.UUID(user_id))
        if user:
            current_other_data = user.other_data or {}
            current_other_data["exit_login"] = datetime.utcnow().isoformat()
            await self.db.users.update_other_data(
                uuid.UUID(user_id), current_other_data
            )
            await self.db.commit()

    async def _log_audit_event(self, user, action: str):
        """Логирование аудита"""
        log_audit_event(
            action=action,
            resource="user",
            details={"user_id": str(user.id)},
            user_id=str(user.id),
        )
        logger.info(f"User {user.id} performed {action} successfully")

    async def _log_audit_event_simple(
        self, user_id: str, action: str, extra: dict = None
    ):
        """Простое логирование аудита"""
        log_audit_event(
            action=action,
            resource="user",
            details=extra or {},
            user_id=user_id,
        )
        logger.info(f"User {user_id} performed {action} successfully")

    def _map_user_to_response(self, user: UserBaseDTO) -> UserResponseDTO:
        last_login_iso = None
        exit_login_iso = None

        if user.other_data:
            try:
                last_login_str = user.other_data.get("last_login")
                if last_login_str:
                    last_login_iso = datetime.fromisoformat(last_login_str).isoformat()

                exit_login_str = user.other_data.get("exit_login")
                if exit_login_str:
                    exit_login_iso = datetime.fromisoformat(exit_login_str).isoformat()
            except (ValueError, TypeError):
                pass

        return UserResponseDTO(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            email=user.email,
            phone=user.phone,
            photo=user.photo,
            roles=user.roles,
            is_active=user.is_active,
            last_login_iso=last_login_iso,
            exit_login_iso=exit_login_iso,
        )

    def _extract_roles(self, roles: str | list) -> list[str]:
        """Извлечение ролей"""
        if isinstance(roles, str):
            return [role.strip() for role in roles.split(",") if role.strip()]

        result = []
        if isinstance(roles, (list, tuple)):
            for role in roles:
                if isinstance(role, str):
                    result.append(role)
                elif hasattr(role, "value"):
                    result.append(role.value)
                else:
                    result.append(str(role))
        return result
