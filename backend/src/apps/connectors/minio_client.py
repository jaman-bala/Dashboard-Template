import uuid
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
import io

from src.core.config import settings


class MinIOClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.public_url = settings.MINIO_PUBLIC_URL
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Создает bucket если он не существует и настраивает публичный доступ"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created bucket: {self.bucket_name}")

            # Настраиваем публичную политику для bucket
            self._set_bucket_policy()
        except S3Error as e:
            print(f"Error creating bucket: {e}")

    def _set_bucket_policy(self):
        """Устанавливает публичную политику для bucket"""
        import json

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*",
                }
            ],
        }

        try:
            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
            print(f"Set public policy for bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"Error setting bucket policy: {e}")

    async def upload_avatar(self, file: UploadFile) -> str:
        """
        Загружает аватар в MinIO и возвращает публичный URL

        Args:
            file: UploadFile объект

        Returns:
            str: Публичный URL загруженного файла

        Raises:
            ValueError: Если файл невалидный
        """
        if not file or not file.filename:
            raise ValueError("Invalid file")

        # Валидация типа файла
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_extension = (
            file.filename.lower().split(".")[-1] if "." in file.filename else ""
        )
        if f".{file_extension}" not in allowed_extensions:
            raise ValueError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        # Читаем содержимое файла
        content = await file.read()

        # Валидация размера (5MB максимум)
        if len(content) > 5 * 1024 * 1024:
            raise ValueError("File size too large. Maximum size: 5MB")

        # Генерируем уникальное имя файла
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        object_name = unique_filename

        try:
            # Загружаем файл в MinIO
            file_data = io.BytesIO(content)
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=len(content),
                content_type=file.content_type or "application/octet-stream",
            )

            # Возвращаем публичный URL
            return f"{self.public_url}/{self.bucket_name}/{object_name}"

        except S3Error as e:
            raise ValueError(f"Failed to upload file: {e}")

    async def delete_avatar(self, url: str) -> bool:
        """
        Удаляет аватар из MinIO

        Args:
            url: URL файла для удаления

        Returns:
            bool: True если файл удален успешно
        """
        try:
            # Извлекаем object_name из URL
            if self.public_url in url:
                object_name = url.replace(f"{self.public_url}/{self.bucket_name}/", "")
                self.client.remove_object(self.bucket_name, object_name)
                return True
            return False
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False

    def get_public_url(self, object_name: str) -> str:
        """
        Возвращает публичный URL для объекта

        Args:
            object_name: Имя объекта в bucket

        Returns:
            str: Публичный URL
        """
        return f"{self.public_url}/{self.bucket_name}/{object_name}"

    def make_bucket_public(self):
        """Принудительно устанавливает публичную политику для bucket"""
        self._set_bucket_policy()


# Глобальный экземпляр MinIO клиента
minio_client = MinIOClient()
