import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from prometheus_client import generate_latest

from src.core.database.database import async_session_maker
from src.core.init import redis_manager
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health Checks"])


class HealthChecker:
    """Класс для проверки состояния различных компонентов системы."""

    def __init__(self):
        self.start_time = datetime.now()

    async def check_database(self) -> Dict[str, Any]:
        """Проверка состояния базы данных."""
        try:
            async with async_session_maker() as session:
                result = await session.execute(text("SELECT 1 as health"))
                row = result.fetchone()

                if row and row.health == 1:
                    return {
                        "status": "healthy",
                        "message": "Database connection successful",
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": "Database query failed",
                        "timestamp": datetime.now().isoformat(),
                    }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def check_redis(self) -> Dict[str, Any]:
        """Проверка состояния Redis."""
        try:
            # Проверяем подключение
            if not redis_manager.redis:
                await redis_manager.connect()

            # Выполняем ping
            await redis_manager.redis.ping()

            # Проверяем возможность записи/чтения
            test_key = "health_check_test"
            test_value = "ok"
            await redis_manager.set(test_key, test_value, expire=10)
            retrieved_value = await redis_manager.get(test_key)

            if retrieved_value and retrieved_value.decode() == test_value:
                return {
                    "status": "healthy",
                    "message": "Redis connection and operations successful",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": "Redis read/write test failed",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def check_disk_space(self) -> Dict[str, Any]:
        """Проверка свободного места на диске."""
        try:
            import shutil

            # Проверяем место для загрузок
            upload_path = settings.LINK_UPLOAD_FILES
            total, used, free = shutil.disk_usage(upload_path)

            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            usage_percent = (used / total) * 100

            if free_gb < 1:  # Меньше 1GB свободного места
                status = "unhealthy"
                message = f"Low disk space: {free_gb:.2f}GB free"
            elif usage_percent > 90:  # Больше 90% использования
                status = "warning"
                message = f"High disk usage: {usage_percent:.1f}%"
            else:
                status = "healthy"
                message = (
                    f"Disk space OK: {free_gb:.2f}GB free ({usage_percent:.1f}% used)"
                )

            return {
                "status": status,
                "message": message,
                "free_space_gb": round(free_gb, 2),
                "total_space_gb": round(total_gb, 2),
                "usage_percent": round(usage_percent, 1),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Disk space check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def check_memory(self) -> Dict[str, Any]:
        """Проверка использования памяти."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent > 95:
                status = "unhealthy"
                message = f"Critical memory usage: {usage_percent:.1f}%"
            elif usage_percent > 85:
                status = "warning"
                message = f"High memory usage: {usage_percent:.1f}%"
            else:
                status = "healthy"
                message = f"Memory usage OK: {usage_percent:.1f}%"

            return {
                "status": status,
                "message": message,
                "usage_percent": round(usage_percent, 1),
                "available_gb": round(memory.available / (1024**3), 2),
                "total_gb": round(memory.total / (1024**3), 2),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Memory check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    async def check_cpu(self) -> Dict[str, Any]:
        """Проверка загрузки CPU."""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 95:
                status = "unhealthy"
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 85:
                status = "warning"
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = "healthy"
                message = f"CPU usage OK: {cpu_percent:.1f}%"

            return {
                "status": status,
                "message": message,
                "usage_percent": round(cpu_percent, 1),
                "core_count": psutil.cpu_count(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"CPU check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"CPU check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }


# Глобальный экземпляр HealthChecker
health_checker = HealthChecker()


@router.get("/", summary="Basic health check")
async def health_check():
    """Базовый health check."""
    return {
        "status": "healthy",
        "message": "Service is running",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - health_checker.start_time),
        "version": settings.PROJECT_VERSION,
    }


@router.get("/detailed", summary="Detailed health check")
async def detailed_health_check():
    """Детальный health check всех компонентов."""
    checks = {
        "database": await health_checker.check_database(),
        "redis": await health_checker.check_redis(),
        "disk_space": await health_checker.check_disk_space(),
        "memory": await health_checker.check_memory(),
        "cpu": await health_checker.check_cpu(),
    }

    # Определяем общий статус
    statuses = [check["status"] for check in checks.values()]
    if "unhealthy" in statuses:
        overall_status = "unhealthy"
        http_status = 503
    elif "warning" in statuses:
        overall_status = "warning"
        http_status = 200
    else:
        overall_status = "healthy"
        http_status = 200

    response_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "uptime": str(datetime.now() - health_checker.start_time),
        "version": settings.PROJECT_VERSION,
        "checks": checks,
        "http_status": http_status,
    }

    return response_data


@router.get("/ready", summary="Readiness probe")
async def readiness_check():
    """Readiness probe для Kubernetes."""
    # Проверяем только критически важные компоненты
    db_check = await health_checker.check_database()
    redis_check = await health_checker.check_redis()

    if db_check["status"] == "healthy" and redis_check["status"] == "healthy":
        return {"status": "ready", "timestamp": datetime.now().isoformat()}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live", summary="Liveness probe")
async def liveness_check():
    """Liveness probe для Kubernetes."""
    # Простая проверка, что приложение отвечает
    return {"status": "alive", "timestamp": datetime.now().isoformat()}


@router.get("/metrics", summary="Prometheus metrics")
async def metrics():
    """Эндпоинт для Prometheus метрик."""
    return generate_latest()
