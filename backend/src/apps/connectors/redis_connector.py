import redis.asyncio as redis


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        self.redis = redis.Redis(host=self.host, port=self.port, decode_responses=True)
        # Проверяем подключение
        await self.redis.ping()

    async def set(self, key: str, value: str, expire: int = None):
        if not self.redis:
            raise ConnectionError("Redis not connected")
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        if not self.redis:
            raise ConnectionError("Redis not connected")
        return await self.redis.get(key)

    async def delete(self, key: str):
        if not self.redis:
            raise ConnectionError("Redis not connected")
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
