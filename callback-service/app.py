import asyncio
import logging
import time
import uvicorn
from threading import Thread

from aio_pika import IncomingMessage

from fastapi import FastAPI

from adapters.rabbit.rabbitpub import AsyncRabbitMQConsumer

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

LOGGER = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def run_consumer():
    consumer = AsyncRabbitMQConsumer("amqp://rmuser:rmpassword@localhost/", "my_queue")
    await consumer.consume()

# Запуск консьюмера
async def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    loop = asyncio.get_event_loop()

    # Запускаем FastAPI и consumer параллельно
    task_fastapi = loop.run_in_executor(None, run_fastapi)
    task_consumer = asyncio.create_task(run_consumer())

    # Ожидаем завершения всех задач
    await task_fastapi
    await task_consumer


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())