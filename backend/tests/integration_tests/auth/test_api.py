import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "firstname, lastname, phone, password, expected_status",
    [
        (
            "John",
            "Doe",
            "1234567890",
            "SecurePass312!*",
            200,
        ),
        (
            "Jane",
            "Smith",
            "0987654321",
            "Weak",  # Ненадежный пароль (можно добавить валидацию паролей в тесты)
            400,
        ),
    ],
)
async def test_auth_flow(
    firstname,
    lastname,
    phone,
    password: str,
    expected_status: int,
    ac: AsyncClient,
):
    # Шаг 1: Получаем токен для авторизации
    resp_login = await ac.post(
        "/auth/login",
        json={"phone": phone, "password": password},
    )
    if resp_login.status_code == 200:
        token = resp_login.cookies.get("access_token")
    else:
        token = None

    # Шаг 2: Регистрация пользователя
    resp_register = await ac.post(
        "/auth/create",
        json={
            "firstname": firstname,
            "lastname": lastname,
            "phone": phone,
            "password": password,
        },
        headers={"Authorization": f"Bearer {token}" if token else ""},
    )

    assert (
        resp_register.status_code == expected_status
    ), f"Ошибка при регистрации: {resp_register.json()}"

    if resp_register.status_code != 200:
        return  # Если регистрация не удалась, выходим из теста

    # Шаг 3: Логин пользователя
    resp_login = await ac.post(
        "/auth/login",
        json={"phone": phone, "password": password},
    )
    assert resp_login.status_code == 200, f"Ошибка при входе: {resp_login.json()}"
    resp_json = resp_login.json()
    assert "access_token" in resp_json, "Ответ должен содержать access_token."

    assert ac.cookies.get("access_token"), "Access-токен должен быть установлен в куки."

    # Дополнительный шаг: Пробуем получить информацию о текущем пользователе
    resp_me = await ac.get("/auth/me")
    assert (
        resp_me.status_code == 200
    ), f"Ошибка при получении данных пользователя: {resp_me.json()}"

    # Проверка, что информация о пользователе соответствует ожидаемой
    user = resp_me.json().get("data")
    assert user, "Информация о пользователе отсутствует."
    assert user["phone"] == phone, "Номер телефона не совпадает с ожидаемым."
    assert "id" in user, "Отсутствует поле 'id' в данных пользователя."
    assert (
        "password" not in user
    ), "Поле 'password' не должно быть в данных пользователя."
    assert (
        "hashed_password" not in user
    ), "Поле 'hashed_password' не должно быть в данных пользователя."

    # Шаг 4: Логаут
    resp_logout = await ac.delete("/auth/logout")
    assert resp_logout.status_code == 200, f"Ошибка при выходе: {resp_logout.json()}"
    assert "access_token" not in ac.cookies, "Токен должен быть удален из cookies."
