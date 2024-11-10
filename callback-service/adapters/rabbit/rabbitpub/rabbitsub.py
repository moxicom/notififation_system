import asyncio
import logging
import time

import aio_pika
from aio_pika import IncomingMessage

LOGGER = logging.getLogger(__name__)

class AsyncRabbitMQConsumer:
    def __init__(self, amqp_url: str, queue_name: str):
        self.amqp_url = amqp_url
        self.queue_name = queue_name

    async def on_message(self, message: IncomingMessage):
        """
        message prcessor
        """
        async with message.process():
            LOGGER.info(f"received message: {message.body.decode()}")
            # Здесь можно добавить вашу логику обработки сообщения
            await self.process_message(message)

    async def process_message(self, message: IncomingMessage):
        await asyncio.sleep(5)

    async def consume(self):
        """
        main method to consume messages
        """
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.queue_name, durable=True)
            await queue.consume(self.on_message)
            LOGGER.info(f"waiting message from queue: {self.queue_name}...")

            # Ожидаем получения сообщений
            await asyncio.Future()  # Блокирует выполнение, пока не завершится работа


