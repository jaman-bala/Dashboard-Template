from src.apps.repositories.mappers.base import DataMapper

from src.apps.models.users import UsersOrm
from src.apps.models.statements import StatementOrm

from src.apps.dto.statements import StatementDTO
from src.apps.dto.users import UserBaseDTO


class UserDataMapper(DataMapper):
    db_model = UsersOrm
    schema = UserBaseDTO


class StatementDataMapper(DataMapper):
    db_model = StatementOrm
    schema = StatementDTO
