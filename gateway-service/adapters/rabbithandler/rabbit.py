# import json
# import logging
#
# import pika
#
# from models import NotificationInfo
# from core.config import config
#
# log = logging.getLogger(__name__)
#
# class RabbitMQProducer:
#     def __init__(self, host: str, input_queue: str = "input_queue_notif", cb_queue: str= "callback_input",
#                  username: str= "rmuser", password: str="rmpassword"):
#         self.host = host
#         self.callback_queue = cb_queue
#         self.input_queue = input_queue
#         self.username = username
#         self.password = password
#         self.connection = None
#         self.channel = None
#
#     def connect(self):
#         """Connects to RabbitMQ."""
#         credentials = pika.PlainCredentials(self.username, self.password)
#
#         self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
#         self.channel = self.connection.channel()
#         self.channel.queue_declare(queue=self.callback_queue, durable=True)
#         self.channel.queue_declare(queue=self.input_queue, durable=True)
#
#     def send_message(self, message: dict):
#         """Send msg to RabbitMQ."""
#         if not self.connection or self.connection.is_closed:
#             self.connect()
#
#         self.channel.basic_publish(
#             exchange='',
#             routing_key=self.callback_queue,
#             body=json.dumps(message),
#             properties=pika.BasicProperties(
#                 delivery_mode=2,
#             )
#         )
#
#     def close_connection(self):
#         """Close con with RabbitMQ."""
#         if self.connection and not self.connection.is_closed:
#             self.connection.close()
#
#     def process_message(self, ch, method, properties, body):
#         """Process received message"""
#         try:
#             if not body:
#                 log.error("Received empty message.")
#                 ch.basic_ack(delivery_tag=method.delivery_tag)
#                 return
#
#             message = json.loads(body)
#             notification = NotificationInfo(**message)
#             log.info(f"Received notification: {notification}")
#
#             self.send_message(notification.model_dump(by_alias=True))
#
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#             log.info("Message processed successfully.")
#
#         except json.JSONDecodeError as e:
#             log.error(f"JSON decode error: {e} - Message: {body}")
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#
#         except Exception as e:
#             log.error(f"Error processing message: {e}")
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#
#     def start_listening(self):
#         """start listening"""
#         self.connect()
#         self.channel.queue_declare(queue=self.input_queue, durable=True)
#         self.channel.basic_consume(queue=self.input_queue, on_message_callback=self.process_message)
#         log.info(f"Waiting for messages from queue {self.callback_queue}. To exit press CTRL+C.")
#         self.channel.start_consuming()
#
#
# def init_rabbit_producer(host: str, input_queue: str, cb_queue: str , username: str ,password: str):
#     global rabbit_producer
#     return RabbitMQProducer(
#         host=host,
#         input_queue=input_queue,
#         cb_queue=cb_queue,
#         username=username,
#         password=password,
#     )
#     # log.info("initialized rabbit")
#
# rabbit_producer = init_rabbit_producer(
#     host=config.RABBIT_HOST,
#     input_queue=config.GATEWAY_INPUT_QUEUE,
#     cb_queue=config.CALLBACK_SERV_QUEUE,
#     password=config.RABBIT_PASSWORD,
#     username=config.RABBIT_USER,
# )
#
# rabbit_producer.connect()

import asyncio
import json
import logging

import aio_pika
import httpx
import pydantic_core
from aio_pika.abc import AbstractIncomingMessage

from core.config import config
from models import NotificationInfo

logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger(__name__)

class AsyncRabbitMQConsumer:
    def __init__(self, amqp_url: str, queue_name: str, callback_service_queue: str):
        self.amqp_url = amqp_url
        self.listen_queue = queue_name
        self.callback_service_queue = callback_service_queue

    async def on_message(self, message: AbstractIncomingMessage):
        """
        message prcessor
        """
        async with message.process():
            LOGGER.info('received message')
            await self.process_message(message)

    async def process_message(self, message: AbstractIncomingMessage):
        """Process received message"""
        try:
            data = NotificationInfo.model_validate_json(json_data=message.body.decode())
        except pydantic_core.ValidationError as ex:
            LOGGER.error(f"failed to parse data {ex}")
            return

        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            try:
                notification = data
                LOGGER.info(f"Received notification: {notification}")

                # self.c(notification.model_dump(by_alias=True))
                queue = await channel.declare_queue(self.callback_service_queue, durable=True)

                await channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps(notification.model_dump(by_alias=True)).encode()),
                    routing_key=queue.name
                )

                await message.ack()
                LOGGER.info("Message processed successfully.")

            except json.JSONDecodeError as e:
                LOGGER.error(f"JSON decode error: {e} - Message: {message.body}")
                await message.ack()

            except Exception as e:
                LOGGER.error(f"Error processing message: {e}")
                await message.ack()

    async def publish_notification(self, message: dict):
        connection = await aio_pika.connect_robust(self.amqp_url)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.callback_service_queue, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=queue.name
            )
            LOGGER.info("Callback sent to RabbitMQ")

    async def consume(self):
        """
        Main method to consume messages
        """
        LOGGER.info("Connecting to RabbitMQ...")
        connection = await aio_pika.connect_robust(self.amqp_url)
        LOGGER.info("Connected to RabbitMQ.")
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.listen_queue, durable=True)
            await queue.consume(self.on_message)
            LOGGER.info(f"Waiting for messages from queue: {self.listen_queue}...")
            await asyncio.Future()  # Keeps the consumer running


rabbit_producer = AsyncRabbitMQConsumer(
        amqp_url=f'amqp://{config.RABBIT_USER}:{config.RABBIT_PASSWORD}@{config.RABBIT_HOST}/',
        queue_name=config.GATEWAY_INPUT_QUEUE,
        callback_service_queue=config.CALLBACK_SERV_QUEUE,
    )

async def new(cfg: config):
    global rabbit_producer
    rabbit_producer = AsyncRabbitMQConsumer(
        amqp_url=f'amqp://{cfg.RABBIT_USER}:{cfg.RABBIT_PASSWORD}@{cfg.RABBIT_HOST}',
        queue_name=cfg.GATEWAY_INPUT_QUEUE,
        callback_service_queue=cfg.CALLBACK_SERV_QUEUE,
    )
    print(config.RABBIT_HOST)
    print(config.RABBIT_USER)
    print(config.RABBIT_PASSWORD)

asyncio.run(new(config))
