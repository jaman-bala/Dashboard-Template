from src.apps.models import StatementOrm
from src.apps.repositories.base import BaseRepository
from src.apps.repositories.mappers.mappers import StatementDataMapper


class StatementsRepository(BaseRepository):
    model = StatementOrm
    mapper = StatementDataMapper
