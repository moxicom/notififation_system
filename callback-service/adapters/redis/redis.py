import redis
import logging
from redis import Redis

from models.models import NotificationDBStatus

LOGGER = logging.getLogger(__name__)

class RedisClient:
    def __init__(self, redis_url: str):
        self.redis_url: str = redis_url
        self.redis: Redis = self.connect(redis_url)

    @staticmethod
    def connect(redis_url: str) -> Redis:
        connection = redis.Redis.from_url(redis_url)
        LOGGER.info("connected to redis")
        return connection

    async def set_data(self, key: str, value: NotificationDBStatus):
        await self.redis.set(key, value.to_json())

    async def get_data(self, key: str) -> [NotificationDBStatus | None]:
        data = await self.redis.get(key)
        if data:
            return NotificationDBStatus.from_json(data.decode())
        return None

    async def close(self):
        await self.redis.close()