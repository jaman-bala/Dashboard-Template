from src.apps.repositories.mappers.types import TModel, TDTO


class DataMapper:
    """Базовый маппер для преобразования между ORM моделями и DTO."""

    db_model: type[TModel] = None
    schema: type[TDTO] = None

    @classmethod
    def map_to_domain_entity(cls, data):
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data):
        return cls.db_model(**data.model_dump())
