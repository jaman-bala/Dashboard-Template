import re
import logging

from typing import Any, Union
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.core.exeptions import SecurityValidationException, DatabaseOperationException

logger = logging.getLogger(__name__)


class SQLProtection:
    """Класс для дополнительной защиты от SQL атак."""

    SQL_INJECTION_PATTERNS = [
        r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)",
        r"(\b(or|and)\s+\d+\s*=\s*\d+)",
        r"(\b(or|and)\s+['\"][^'\"]*['\"]\s*=\s*['\"][^'\"]*['\"])",
        r"(--|\#|\/\*|\*\/)",
        r"(\b(script|javascript|vbscript)\b)",
        r"(\b(benchmark|sleep|waitfor|delay)\b)",
        r"(\b(load_file|into\s+outfile|into\s+dumpfile)\b)",
        r"(\b(char|ascii|ord|hex|unhex)\b)",
        r"(\b(substring|mid|left|right|reverse)\b)",
        r"(\b(concat|group_concat)\b)",
        r"(\b(version|database|user|schema)\b)",
        r"(\b(information_schema|mysql|sys)\b)",
        r"(\b(union\s+select|union\s+all\s+select)\b)",
        r"(\b(select\s+.*\s+from\s+.*\s+where\s+.*\s*=\s*.*\s*or\s+.*\s*=\s*.*)\b)",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
    ]

    @classmethod
    def validate_input(cls, value: Any, input_type: str = "general") -> bool:
        """Валидация входных данных на предмет потенциальных атак."""
        if value is None:
            return True

        str_value = str(value)

        if len(str_value) > 10000:
            logger.warning(f"Input too long: {len(str_value)} characters")
            return False

        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, str_value, re.IGNORECASE):
                logger.warning(
                    f"Potential SQL injection detected in {input_type}: {pattern}"
                )
                return False

        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, str_value, re.IGNORECASE):
                logger.warning(f"Potential XSS detected in {input_type}: {pattern}")
                return False

        return True

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """Очистка строки от потенциально опасных символов."""
        if not value:
            return ""

        value = value[:max_length]

        dangerous_chars = ["<", ">", '"', "'", "&", ";", "(", ")", "|", "`", "$"]
        for char in dangerous_chars:
            value = value.replace(char, "")

        value = re.sub(r"\s+", " ", value).strip()

        return value

    @classmethod
    def validate_query_params(cls, params: dict[str, Any]) -> dict[str, Any]:
        """Валидация параметров запроса."""
        validated_params = {}

        for key, value in params.items():
            if cls.validate_input(value, f"query_param_{key}"):
                if isinstance(value, str):
                    validated_params[key] = cls.sanitize_string(value)
                else:
                    validated_params[key] = value
            else:
                logger.warning(f"Invalid query parameter: {key} = {value}")
                raise SecurityValidationException(f"Invalid parameter: {key}")

        return validated_params

    @classmethod
    def validate_filter_params(cls, filters: dict[str, Any]) -> dict[str, Any]:
        """Валидация параметров фильтрации."""
        allowed_operators = [
            "eq",
            "ne",
            "gt",
            "gte",
            "lt",
            "lte",
            "like",
            "ilike",
            "in",
            "not_in",
        ]
        validated_filters = {}

        for field, value in filters.items():
            if not cls.validate_input(field, "filter_field"):
                logger.warning(f"Invalid filter field name: {field}")
                continue

            if isinstance(value, dict):
                operator = value.get("operator")
                val = value.get("value")

                if operator not in allowed_operators:
                    logger.warning(f"Invalid filter operator: {operator}")
                    continue

                if cls.validate_input(val, f"filter_value_{field}"):
                    validated_filters[field] = value
                else:
                    logger.warning(f"Invalid filter value: {field} = {val}")
            else:
                if cls.validate_input(value, f"filter_value_{field}"):
                    validated_filters[field] = value
                else:
                    logger.warning(f"Invalid filter value: {field} = {value}")

        return validated_filters

    @classmethod
    def safe_execute_query(
        cls, session, query: Union[str, text], params: dict[str, Any] = None
    ) -> Any:
        """Безопасное выполнение SQL запроса."""
        try:
            if params:
                params = cls.validate_query_params(params)

            if isinstance(query, str):
                if not cls.validate_input(query, "sql_query"):
                    raise SecurityValidationException("Invalid query")
                query = text(query)

            result = session.execute(query, params or {})
            return result

        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise DatabaseOperationException(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise DatabaseOperationException(f"Query execution failed: {str(e)}")

    @classmethod
    def validate_pagination_params(
        cls, page: int = 1, per_page: int = 20
    ) -> tuple[int, int]:
        """Валидация параметров пагинации."""
        per_page = min(max(per_page, 1), 100)
        page = max(page, 1)

        return page, per_page

    @classmethod
    def validate_sort_params(
        cls, sort_by: str, sort_order: str = "asc"
    ) -> tuple[str, str]:
        """Валидация параметров сортировки."""
        allowed_fields = ["id", "created_at", "updated_at", "name", "email", "phone"]

        if sort_by not in allowed_fields:
            sort_by = "created_at"

        if sort_order.lower() not in ["asc", "desc"]:
            sort_order = "asc"

        return sort_by, sort_order


sql_protection = SQLProtection()
