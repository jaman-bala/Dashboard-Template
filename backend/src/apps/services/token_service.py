"""Сервис управления токенами"""

import uuid
from src.core.security.jwt_manager import jwt_manager
from src.domain.exceptions import InvalidTokenException, ExpiredTokenException


class TokenService:
    """Сервис управления токенами"""

    async def create_token(
        self, user_id: uuid.UUID, roles: list[str], token_type: str
    ) -> str:
        """Создание токена"""
        payload = jwt_manager.create_token_payload(
            user_id=str(user_id), roles=roles, token_type=token_type
        )
        return await jwt_manager.create_token(payload)

    async def validate_token(self, token: str, token_type: str) -> dict:
        """Валидация токена"""
        try:
            return await jwt_manager.validate_token(token, token_type)
        except Exception as e:
            if "expired" in str(e):
                raise ExpiredTokenException
            raise InvalidTokenException

    async def refresh_access_token(self, refresh_token: str, db) -> str:
        """Обновление access токена"""
        try:
            payload = await jwt_manager.validate_token(refresh_token, "refresh")
        except Exception:
            raise InvalidTokenException

        user_id = uuid.UUID(payload["user_id"])

        # Получаем актуальные данные пользователя
        user = await db.users.get_one_or_none(id=user_id)
        if not user:
            raise InvalidTokenException

        roles = self._extract_roles(user.roles)
        return await self.create_token(user_id, roles, "access")

    async def logout_user(self, access_token: str = None, user_id: str = None) -> None:
        """Выход пользователя"""
        if access_token:
            await jwt_manager.blacklist_token(access_token)
        if user_id:
            await jwt_manager.blacklist_user_tokens(user_id)

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
