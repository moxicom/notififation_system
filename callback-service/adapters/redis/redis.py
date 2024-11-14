import redis
import logging
import json
from redis import Redis
from typing import List

from config import config
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

    def set_data(self, key: str, values: List[NotificationDBStatus]):
        json_data = json.dumps([value.to_json() for value in values])
        self.redis.set(key, json_data, ex=config.CALLBACK_SERVICE_RABBIT_TTL)

    def get_data(self, key: str) -> List[NotificationDBStatus]:
        json_data: str = self.redis.get(key)
        if json_data:
            status_dicts = json.loads(json_data)
            return [NotificationDBStatus.from_json(status) for status in status_dicts]
        return []

    async def close(self):
        await self.redis.close()

redis_client = RedisClient('redis://'+ config.REDIS_HOST + ':' + config.REDIS_PORT)

def get_redis_client() -> RedisClient:
    return redis_client