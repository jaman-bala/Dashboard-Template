import re
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal


class Settings(BaseSettings):
    PROJECT_NAME: str = Field(
        default="Dashboard Template", description="Название проекта"
    )
    PROJECT_VERSION: str = Field(default="1.0.0", description="Версия проекта")
    MODE: Literal["PROD", "DEV", "test"] = Field(
        default="test", description="Режим работы"
    )

    POSTGRES_HOST: str = Field(description="Хост базы данных")
    POSTGRES_PORT: int = Field(description="Порт базы данных")
    POSTGRES_USER: str = Field(description="Пользователь базы данных")
    POSTGRES_PASSWORD: str = Field(description="Пароль базы данных")
    POSTGRES_DB: str = Field(description="Название базы данных")

    REDIS_HOST: str = Field(description="Хост Redis")
    REDIS_PORT: int = Field(description="Порт Redis")

    @property
    def REDIS_URL(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    JWT_SECRET_KEY: str = Field(description="Секретный ключ для JWT")
    JWT_ALGORITHM: str = Field(description="Алгоритм JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        description="Время жизни access token в минутах"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        description="Время жизни refresh token в днях"
    )

    PASSWORD_REGEX_PATTERN: str = Field(
        default=r"^[a-zA-Z\d@$!%*?&]{8,72}$",
        description="Паттерн для валидации паролей",
    )
    PHONE_REGEX_PATTERN: str = Field(
        default=r"^\+?\d{10,15}$", description="Паттерн для валидации телефонов"
    )
    EMAIL_REGEX_PATTERN: str = Field(
        default=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Паттерн для валидации email",
    )

    @property
    def PASSWORD_REGEX(self):
        return re.compile(self.PASSWORD_REGEX_PATTERN)

    @property
    def PHONE_REGEX(self):
        return re.compile(self.PHONE_REGEX_PATTERN)

    @property
    def EMAIL_REGEX(self):
        return re.compile(self.EMAIL_REGEX_PATTERN)

    LINK_IMAGES: str = Field(description="Путь для изображений")
    LINK_UPLOAD_FILES: str = Field(description="Путь для загружаемых файлов")
    LINK_UPLOAD_PHOTO: str = Field(description="Путь для фотографий")

    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:8080"],
        description="Разрешенные CORS origins",
    )

    MAX_FILE_SIZE_MB: int = Field(
        default=5, ge=1, description="Максимальный размер файла в MB"
    )
    ALLOWED_FILE_EXTENSIONS: list[str] = Field(
        default=["jpg", "jpeg", "png", "gif"],
        description="Разрешенные расширения файлов",
    )

    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO endpoint")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO secret key")
    MINIO_BUCKET_NAME: str = Field(default="avatars", description="MinIO bucket name")
    MINIO_SECURE: bool = Field(default=False, description="Use HTTPS for MinIO")
    MINIO_PUBLIC_URL: str = Field(
        default="http://localhost:9000", description="Public URL for MinIO"
    )

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("POSTGRES_PORT", "REDIS_PORT")
    @classmethod
    def validate_ports(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    model_config = SettingsConfigDict(
        env_file="../infra/envs/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
