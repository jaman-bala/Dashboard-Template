import uuid
from src.services.auth import AuthService
from src.config import settings
import jwt


def test_create_and_decode_access_token():
    """
    Тестирует создание и декодирование access-токена.
    """
    data = {"user_id": str(uuid.uuid4()), "roles": ["USER"]}

    # Создание токена
    auth_service = AuthService(
        None
    )  # Замените None на mock базы данных, если требуется
    jwt_token = auth_service.create_access_token(data)

    assert jwt_token, "Токен не должен быть пустым."
    assert isinstance(jwt_token, str), "Токен должен быть строкой."

    # Декодирование токена
    payload = jwt.decode(
        jwt_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload, "Payload не должен быть пустым."
    assert payload["user_id"] == data["user_id"], "user_id должен совпадать."
    assert "exp" in payload, "Payload должен содержать дату истечения срока действия."
    assert "roles" in payload, "Payload должен содержать роли."


def test_create_refresh_token():
    """
    Тестирует создание refresh-токена.
    """
    data = {"user_id": str(uuid.uuid4())}
    auth_service = AuthService(None)
    refresh_token = auth_service.set_refresh_token({}, data)

    assert refresh_token, "Refresh-токен не должен быть пустым."
    payload = jwt.decode(
        refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["user_id"] == data["user_id"], "user_id должен совпадать."
    assert "exp" in payload, "Payload должен содержать дату истечения срока действия."
