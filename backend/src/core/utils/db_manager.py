from src.apps.repositories.statements import StatementsRepository
from src.apps.repositories.users import UsersRepository
from src.apps.services.cache_service import CacheServiceFactory
from src.core.init import redis_manager


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        cache_service = CacheServiceFactory.create_redis_cache(redis_manager)

        self.users = UsersRepository(self.session, cache_service)
        self.statements = StatementsRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
