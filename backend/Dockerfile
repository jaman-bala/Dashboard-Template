FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc libpq-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Ставим uv
RUN pip install --no-cache-dir uv

# Копируем проект
COPY . .

# Устанавливаем зависимости
RUN uv sync --frozen

# Применяем миграции и запускаем сервер
CMD ["sh", "-c", "python -m alembic upgrade head && python -m uvicorn src.main:app --host 0.0.0.0 --port 8080"]
