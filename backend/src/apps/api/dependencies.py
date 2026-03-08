import uuid
from fastapi import Depends, Query, Request, HTTPException
from pydantic import BaseModel
from typing import Annotated

from src.core.database.database import async_session_maker
from src.core.exeptions import InvalidTokenException
from src.apps.services.auth import AuthService
from src.core.utils.db_manager import DBManager


class PaginationParamsDTO(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=100)]


PaginationDep = Annotated[PaginationParamsDTO, Depends()]


def get_db_manager():
    return DBManager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]


def get_token(request: Request) -> str:
    # Сначала проверяем заголовок Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Убираем "Bearer " из начала

    # Если нет заголовка, проверяем cookies
    token = request.cookies.get("access_token", None)
    if not token:
        raise HTTPException(
            status_code=401, detail="You did not provide an access token"
        )
    return token


async def get_current_user_id(db: DBDep, token: str = Depends(get_token)) -> uuid.UUID:
    try:
        # Создаем временный AuthService для декодирования токена
        auth_service = AuthService(db)
        data = await auth_service.decode_access_token(token)
        return uuid.UUID(data["user_id"])
    except InvalidTokenException:
        raise HTTPException(status_code=401, detail="Incorrect access token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID format")


async def get_current_is_superuser(db: DBDep, token: str = Depends(get_token)) -> bool:
    try:
        auth_service = AuthService(db)
        data = await auth_service.decode_access_token(token)
        return "SUPERUSER" in data.get("roles", [])
    except InvalidTokenException:
        raise HTTPException(status_code=401, detail="Incorrect access token")


async def get_current_admin(db: DBDep, token: str = Depends(get_token)) -> bool:
    try:
        auth_service = AuthService(db)
        data = await auth_service.decode_access_token(token)
        return "ADMIN" in data.get("roles", []) or "SUPERUSER" in data.get("roles", [])
    except InvalidTokenException:
        raise HTTPException(status_code=401, detail="Incorrect access token")


async def get_current_user(db: DBDep, token: str = Depends(get_token)) -> dict:
    try:
        auth_service = AuthService(db)
        data = await auth_service.decode_access_token(token)
        return data
    except InvalidTokenException:
        raise HTTPException(status_code=401, detail="Incorrect access token")


UserIdDep = Annotated[uuid.UUID, Depends(get_current_user_id)]
RoleSuperuserDep = Annotated[bool, Depends(get_current_is_superuser)]
RoleAdminDep = Annotated[bool, Depends(get_current_admin)]
UserDep = Annotated[dict, Depends(get_current_user)]
