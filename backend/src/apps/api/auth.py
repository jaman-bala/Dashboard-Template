import uuid
from fastapi import APIRouter, Response, Request, File, UploadFile

from src.apps.api.dependencies import UserIdDep, DBDep, RoleSuperuserDep, RoleAdminDep
from src.core.exeptions import (
    InvalidTokenException,
    TokenValidationException,
    RolesAdminHTTPException,
)
from src.apps.dto.users import (
    UserRequestLoginDTO,
    UserRequestAddDTO,
    UserRequestUpdatePasswordDTO,
    RefreshTokenRequestDTO,
    UserUpdateRequestDTO,
    UserResponseDTO,
)
from src.apps.services.auth import AuthService
from src.apps.middleware.rate_limiting import (
    login_rate_limit,
    register_rate_limit,
    password_reset_rate_limit,
)
from src.apps.connectors.minio_client import minio_client


router = APIRouter(prefix="/auth", tags=["Authorization and authentication"])


@router.post("/create", summary="Creating a user 👨🏽‍💻")
@register_rate_limit
async def register_user(
    request: Request,
    data: UserRequestAddDTO,
    db: DBDep,
):
    users = await AuthService(db).register_user(data)
    return UserResponseDTO.model_validate(users)


@router.post("/login", summary="Login 👨🏽‍💻")
@login_rate_limit
async def login_user(
    request: Request,
    data: UserRequestLoginDTO,
    response: Response,
    db: DBDep,
):
    return await AuthService(db).login_user(data)


@router.get("/me", summary="My profile👨🏽‍💻")
async def get_me(
    current_data: UserIdDep,
    db: DBDep,
):
    return await AuthService(db).get_me(current_data)


@router.get("/get_users_by_id/{user_id}", summary="Request by ID user")
async def get_users_by_id(
    role_admin: RoleSuperuserDep,
    user_id: uuid.UUID,
    db: DBDep,
):
    if not role_admin:
        raise RolesAdminHTTPException
    return await AuthService(db).get_user_by_id(user_id)


@router.get("/get_all_users", summary="Output of all users 👨🏽‍💻")
async def get_all_users(
    role_admin: RoleSuperuserDep,
    db: DBDep,
):
    if not role_admin:
        raise RolesAdminHTTPException
    return await AuthService(db).get_all_users()


@router.delete("/logout", summary="Logout 👨🏽‍💻")
async def logout_user(
    request: Request,
    response: Response,
    db: DBDep,
):
    # Получаем токен из Authorization header или cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header[7:]  # Убираем "Bearer "

    # Получаем user_id из токена если он есть
    user_id = None
    if access_token:
        try:
            auth_service = AuthService(db)
            payload = await auth_service.decode_access_token(access_token)
            user_id = payload.get("user_id")
        except InvalidTokenException:
            raise TokenValidationException

    # Выполняем logout с blacklist
    await AuthService(db).logout_user(access_token, user_id)

    return {"message": "Logout success"}


@router.patch("/update/{user_id}", summary="Partial change 👨🏽‍💻")
async def update_user(
    user_id: uuid.UUID,
    role_admin: RoleSuperuserDep,
    db: DBDep,
    data: UserUpdateRequestDTO,
):
    if not role_admin:
        raise RolesAdminHTTPException
    return await AuthService(db).patch_user(user_id, data)


@router.patch("/update_avatar/{user_id}", summary="Update user avatar 👨🏽‍💻")
async def update_user_avatar(
    user_id: uuid.UUID,
    role_admin: RoleAdminDep,
    db: DBDep,
    photo: UploadFile = File(None),
):
    if not role_admin:
        raise RolesAdminHTTPException

    photo_url = None
    if photo and photo.filename:
        photo_url = await minio_client.upload_avatar(photo)

    return await AuthService(db).patch_avatars(user_id, photo_url)


@router.delete("/{user_id}", summary="Deleting a user 👨🏽‍💻")
async def delete_user(user_id: uuid.UUID, role_admin: RoleSuperuserDep, db: DBDep):
    if not role_admin:
        raise RolesAdminHTTPException
    await AuthService(db).delete_user(user_id)
    return {"message": "User deleted"}


@router.put("/change_password/{user_id}", summary="Password reset")
@password_reset_rate_limit
async def change_password(
    request: Request,
    user_id: uuid.UUID,
    role_admin: RoleSuperuserDep,
    data: UserRequestUpdatePasswordDTO,
    db: DBDep,
):
    if not role_admin:
        raise RolesAdminHTTPException
    await AuthService(db).change_password(user_id, data)
    return {"message": "Password successfully changed"}


@router.post("/setup_minio", summary="Setup MinIO bucket public access")
async def setup_minio_public_access(role_admin: RoleSuperuserDep):
    """Настраивает публичный доступ к MinIO bucket для аватаров"""
    if not role_admin:
        raise RolesAdminHTTPException

    minio_client.make_bucket_public()
    return {"message": "MinIO bucket configured for public access"}


@router.post("/refresh", summary="Refresh access_token using refresh_token")
async def refresh_access_token(
    request: Request,
    response: Response,
    data: RefreshTokenRequestDTO,
    db: DBDep,
):
    refresh_token = request.cookies.get("refresh_token")
    result = await AuthService(db).refresh_access_token(refresh_token, response)
    return {
        "status": "Token updated",
        "access_token": result["access_token"],
    }
