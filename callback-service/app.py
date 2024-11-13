import asyncio
import logging
import time
import uvicorn
from threading import Thread

from aio_pika import IncomingMessage

from fastapi import FastAPI

from adapters.httpserver import create_rest_handler
from adapters.rabbit.rabbitpub import AsyncRabbitMQConsumer
from adapters.redis.redis import RedisClient

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

LOGGER = logging.getLogger(__name__)

http_server = create_rest_handler(8082)

def run_fastapi():
    uvicorn.run(http_server.handler, host='0.0.0.0', port=8000)

async def run_consumer():
    consumer = AsyncRabbitMQConsumer('amqp://rmuser:rmpasswrod@localhost/', 'my_queue')
    await consumer.consume()

async def main():
    loop = asyncio.get_event_loop()

    task_fastapi = loop.run_in_executor(None, run_fastapi)
    task_consumer = asyncio.create_task(run_consumer())

    await task_fastapi
    await task_consumer


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
