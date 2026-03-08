import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.utils.exception_mapper import ExceptionMapper

logger = logging.getLogger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для глобальной обработки исключений."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as http_exc:
            # Если это уже HTTPException, пропускаем как есть
            return JSONResponse(
                status_code=http_exc.status_code, content={"detail": http_exc.detail}
            )
        except Exception as e:
            # Маппим все остальные исключения
            logger.error(f"Unhandled exception: {type(e).__name__}: {str(e)}")
            http_exception = ExceptionMapper.handle_service_exception(e)

            # Определяем тип ответа в зависимости от статуса
            if http_exception.status_code == 400:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Validation Error",
                        "message": "Переданы некорректные данные",
                        "details": [],
                    },
                )
            elif http_exception.status_code == 409:
                # Conflict - дубликаты и другие нарушения целостности
                # Используем детальную информацию из исключения если она есть
                http_exception.detail
                if (
                    isinstance(http_exception.detail, dict)
                    and "field" in http_exception.detail
                ):
                    # Новый формат с указанием поля
                    return JSONResponse(
                        status_code=409,
                        content=http_exception.detail,
                    )
                else:
                    # Старый формат для обратной совместимости
                    return JSONResponse(
                        status_code=409,
                        content={
                            "error": "Conflict",
                            "message": http_exception.detail,
                            "details": None,
                        },
                    )
            else:
                # Все остальные ошибки
                return JSONResponse(
                    status_code=http_exception.status_code,
                    content={
                        "error": "Error",
                        "message": http_exception.detail,
                        "details": None,
                    },
                )
