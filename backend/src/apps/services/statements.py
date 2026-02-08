import uuid

from src.core.exeptions import StatementNotFoundException
from src.apps.dto.statements import StatementAddRequestDTO, StatementPatchDTO
from src.apps.services.base import BaseService


class StatementsService(BaseService):
    async def create_statements(self, data: StatementAddRequestDTO):
        await self.db.statements.add(data)
        return data

    async def get_statements(self):
        statements = await self.db.statements.get_all()
        return statements

    async def get_statements_by_id(self, statement_id: uuid.UUID):
        statements = await self.db.statements.get_one_or_none(id=statement_id)
        return statements

    async def patch_statement(
        self,
        statement_id: uuid.UUID,
        data: StatementPatchDTO,
        exclude_unset: bool = False,
    ):
        statements = await self.db.statements.get_one_or_none(id=statement_id)
        if not statements:
            raise StatementNotFoundException
        await self.db.statements.update(
            data, exclude_unset=exclude_unset, id=statement_id
        )
        return statements

    async def delete_statement(self, statement_id: uuid.UUID):
        await self.db.statements.delete(id=statement_id)
