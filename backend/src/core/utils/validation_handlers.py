import logging
from pydantic import ValidationError
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError | ValidationError
):
    """
    Глобальный обработчик ошибок валидации.
    Ловит как ошибки FastAPI (RequestValidationError), так и ручные ошибки Pydantic (ValidationError).
    """
    errors = []
    for error in exc.errors():
        # Формируем путь к полю (например, body.email)
        field = ".".join([str(loc) for loc in error["loc"][1:]])
        msg = error["msg"]
        errors.append({"field": field, "message": msg, "type": error.get("type")})

    logger.warning(f"Validation error for {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation Error",
            "message": "Переданы некорректные данные",
            "details": errors,
        },
    )
