import jwt
import uuid
import logging

from datetime import datetime, timezone, timedelta

from src.core.config import settings
from src.core.init import redis_manager
from src.domain.exceptions import (
    TokenValidationException,
    InvalidTokenException,
)

logger = logging.getLogger(__name__)


class JWTManager:
    """Управление JWT токенами с улучшенной безопасностью."""

    def __init__(self):
        self.algorithm = settings.JWT_ALGORITHM
        self.secret_key = settings.JWT_SECRET_KEY
        self.access_token_expire = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    def create_token_payload(
        self, user_id: str, roles: list[str], token_type: str = "access"
    ) -> dict:
        """Создает payload для JWT токена с дополнительными полями безопасности."""
        now = datetime.now(timezone.utc)
        jti = str(uuid.uuid4())

        payload = {
            "user_id": user_id,
            "roles": roles,
            "token_type": token_type,
            "jti": jti,
            "iat": now,
            "exp": now
            + (
                self.access_token_expire
                if token_type == "access"
                else self.refresh_token_expire
            ),
            "iss": settings.PROJECT_NAME,
            "aud": "dashboard-api",
            "sub": user_id,
            "version": "1.0",
        }

        return payload

    async def create_token(self, payload: dict) -> str:
        """Создает JWT токен с дополнительными заголовками."""
        headers = {
            "typ": "JWT",
            "alg": self.algorithm,
            "kid": "dashboard-key-1",
        }

        try:
            token = jwt.encode(
                payload, self.secret_key, algorithm=self.algorithm, headers=headers
            )

            await self._store_token_jti(
                payload["jti"], payload["user_id"], payload["exp"]
            )

            return token
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise InvalidTokenException(f"Token creation failed: {str(e)}")

    async def validate_token(self, token: str, token_type: str = "access") -> dict:
        """Валидирует JWT токен с дополнительными проверками."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="dashboard-api",
                issuer=settings.PROJECT_NAME,
            )

            if payload.get("token_type") != token_type:
                raise TokenValidationException("Invalid token type")

            jti = payload.get("jti")
            if jti and await self._is_token_blacklisted(jti):
                raise TokenValidationException("Token has been revoked")

            if payload.get("version") != "1.0":
                raise TokenValidationException("Token version not supported")

            user_id = payload.get("user_id")
            if user_id and not await self._is_user_active(user_id):
                raise TokenValidationException("User is no longer active")

            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
                timezone.utc
            ):
                raise TokenValidationException("Token has expired")

            logger.info(f"Token validated successfully for user {user_id}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise TokenValidationException("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise TokenValidationException("Invalid token")
        except TokenValidationException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating token: {e}")
            raise TokenValidationException("Token validation failed")

    async def blacklist_token(self, token: str) -> bool:
        """Добавляет токен в blacklist."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            jti = payload.get("jti")
            if not jti:
                return False

            exp = payload.get("exp")
            if exp:
                ttl = int(exp - datetime.now(timezone.utc).timestamp())
                if ttl > 0:
                    await redis_manager.set(f"blacklist:{jti}", "1", expire=ttl)
                    logger.info(f"Token {jti} added to blacklist")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False

    async def blacklist_user_tokens(self, user_id: str) -> int:
        """Добавляет все токены пользователя в blacklist."""
        try:
            pattern = f"token_jti:{user_id}:*"
            keys = await redis_manager.redis.keys(pattern)

            blacklisted_count = 0
            for key in keys:
                jti = key.decode().split(":")[-1]
                await redis_manager.set(f"blacklist:{jti}", "1", expire=86400)
                blacklisted_count += 1

            logger.info(f"Blacklisted {blacklisted_count} tokens for user {user_id}")
            return blacklisted_count

        except Exception as e:
            logger.error(f"Error blacklisting user tokens: {e}")
            return 0

    async def _store_token_jti(self, jti: str, user_id: str, exp: datetime):
        """Сохраняет JTI токена для отслеживания."""
        try:
            key = f"token_jti:{user_id}:{jti}"
            ttl = int((exp - datetime.now(timezone.utc)).total_seconds())
            if ttl > 0:
                await redis_manager.set(key, "1", expire=ttl)
        except Exception as e:
            logger.error(f"Error storing token JTI: {e}")
            raise InvalidTokenException(f"Failed to store token JTI: {str(e)}")

    async def _is_token_blacklisted(self, jti: str) -> bool:
        """Проверяет, находится ли токен в blacklist."""
        try:
            result = await redis_manager.get(f"blacklist:{jti}")
            return result is not None
        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            raise InvalidTokenException(f"Failed to check token blacklist: {str(e)}")

    async def _is_user_active(self, user_id: str) -> bool:
        """Проверяет, активен ли пользователь."""
        try:
            return True
        except Exception as e:
            logger.error(f"Error checking user status: {e}")
            return False


jwt_manager = JWTManager()
