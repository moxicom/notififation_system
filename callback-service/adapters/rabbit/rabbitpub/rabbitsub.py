import asyncio
import json
import logging
import time

import aio_pika
import httpx
import pydantic_core
from aio_pika import IncomingMessage
from aio_pika.abc import AbstractMessage, AbstractIncomingMessage

from adapters.redis.redis import RedisClient
from models import NotificationInfo
from models.models import SenderType, NotificationDBStatus

LOGGER = logging.getLogger(__name__)

class AsyncRabbitMQConsumer:
    def __init__(self, amqp_url: str, queue_name: str, redis_client: RedisClient):
        self.amqp_url = amqp_url
        self.listen_queue = queue_name
        self.redis_client: RedisClient = redis_client

    async def on_message(self, message: AbstractIncomingMessage):
        """
        message prcessor
        """
        async with message.process():
            LOGGER.info(f"received message: {message.body.decode()}")
            await self.process_message(message)

    async def process_message(self, message: AbstractIncomingMessage):
        try:
            data = NotificationInfo.model_validate_json(json_data=message.body.decode())
        except pydantic_core.ValidationError as ex:
            LOGGER.error(f"failed to parse data {ex}")
            return

        try:
            for login in data.logins:
                if data.sender_type.SMS:
                    await self.redis_client.set_data(data.message_id, NotificationDBStatus(
                        message_id=data.message_id,
                        login=login,
                        sender_type="SMS",
                        status=False,
                    ))
                if data.sender_type.EMAIL:
                    await self.redis_client.set_data(data.message_id, NotificationDBStatus(
                        message_id=data.message_id,
                        login=login,
                        sender_type="EMAIL",
                        status=False,
                    ))
        except Exception as ex:
            LOGGER.error(f'failed to set to redis {ex}')

        # TODO push to redis

        # TODO send to senders

        # TODO wait senders callback.

        await self.wait_for_callbacks(data)

    async def wait_for_callbacks(self, data: NotificationInfo):
        await asyncio.sleep(5) # TIMEOUT
        a = NotificationDBStatus(data.message_id, "login1",  "SMS", False) # TODO
        b = NotificationDBStatus(data.message_id, "login2",  "MAIL", True) # TODO
        result = [a, b]
        if data.callback_type.http != "":
            await self.send_callback_http(data.callback_type.http, result)
        if data.callback_type.queue != "":
            await self.send_callback_rabbitmq(data.callback_type.queue, result)

    @staticmethod
    async def send_callback_http(url: str, result: list[NotificationDBStatus]):
        data = {"result": [status.__dict__ for status in result]}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)  # Directly send the dict instead of json.dumps
            LOGGER.info(f"Callback sent, status code: {response.status_code}")

    async def send_callback_rabbitmq(self, queue: str, result: list[NotificationDBStatus]):
        connection = await aio_pika.connect_robust(self.amqp_url)
        # Convert NotificationDBStatus objects to dictionaries for JSON serialization
        serialized_result = [status.__dict__ for status in result]
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue("callback_result_queue", durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(serialized_result).encode()),
                routing_key=queue.name
            )
            LOGGER.info("Callback sent to RabbitMQ")

    async def consume(self):
        """
        main method to consume messages
        """
        LOGGER.info("connecting to rabbit")
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.listen_queue, durable=True)
            await queue.consume(self.on_message)
            LOGGER.info(f"waiting message from queue: {self.listen_queue}...")

            # Ожидаем получения сообщений
            await asyncio.Future()  # Блокирует выполнение, пока не завершится работа


