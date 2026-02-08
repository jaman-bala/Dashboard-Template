import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json

from src.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON форматер для структурированного логирования."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }

        # Добавляем дополнительные поля если они есть
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_entry["ip_address"] = record.ip_address
        if hasattr(record, "endpoint"):
            log_entry["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "response_time"):
            log_entry["response_time"] = record.response_time

        # Добавляем exception info если есть
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


class SecurityFilter(logging.Filter):
    """Фильтр для удаления чувствительной информации из логов."""

    SENSITIVE_FIELDS = [
        "password",
        "token",
        "secret",
        "key",
        "auth",
        "credential",
        "hashed_password",
        "access_token",
        "refresh_token",
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        # Удаляем чувствительные данные из сообщений
        message = record.getMessage()
        for field in self.SENSITIVE_FIELDS:
            message = message.replace(field, "[REDACTED]")

        # Обновляем запись
        record.msg = message
        record.args = ()

        return True


def setup_logging():
    """Настройка логирования для приложения."""

    # Создаем директории для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Определяем уровень логирования в зависимости от режима
    log_level = logging.INFO if settings.MODE == "PROD" else logging.DEBUG

    # Создаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Очищаем существующие обработчики
    root_logger.handlers.clear()

    # 1. Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if settings.MODE == "PROD":
        # В продакшене используем JSON формат
        console_formatter = JSONFormatter()
    else:
        # В разработке используем читаемый формат
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(SecurityFilter())
    root_logger.addHandler(console_handler)

    # 2. Файловый обработчик для всех логов
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(SecurityFilter())
    root_logger.addHandler(file_handler)

    # 3. Обработчик для ошибок
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    error_handler.addFilter(SecurityFilter())
    root_logger.addHandler(error_handler)

    # 4. Обработчик для безопасности
    security_handler = logging.handlers.RotatingFileHandler(
        log_dir / "security.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=20,
        encoding="utf-8",
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(security_handler)

    # 5. Обработчик для аудита
    audit_handler = logging.handlers.RotatingFileHandler(
        log_dir / "audit.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=30,
        encoding="utf-8",
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(audit_handler)

    # Настройка логгеров для внешних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)

    # Создаем специальные логгеры
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)

    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(audit_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Получить логгер с заданным именем."""
    return logging.getLogger(name)


def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    user_id: str = None,
    ip_address: str = None,
):
    """Логирование событий безопасности."""
    security_logger = logging.getLogger("security")

    extra = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        **details,
    }

    security_logger.warning(f"Security event: {event_type}", extra=extra)


def log_audit_event(
    action: str, resource: str, details: Dict[str, Any], user_id: str = None
):
    """Логирование аудиторских событий."""
    audit_logger = logging.getLogger("audit")

    extra = {"action": action, "resource": resource, "user_id": user_id, **details}

    audit_logger.info(f"Audit: {action} on {resource}", extra=extra)


def log_performance_metric(
    metric_name: str, value: float, unit: str = "ms", details: Dict[str, Any] = None
):
    """Логирование метрик производительности."""
    perf_logger = logging.getLogger("performance")

    extra = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        **(details or {}),
    }

    perf_logger.info(f"Performance: {metric_name} = {value}{unit}", extra=extra)


# Инициализация логирования
setup_logging()
