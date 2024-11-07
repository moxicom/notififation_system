import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from adapters.httpserver import create_rest_handler

from adapters.rabbithandler import init_rabbit_producer, rabbit_producer
from core.config import config


# Функция для запуска HTTP сервера
def run_http_server(port: int):
    handler = create_rest_handler(port)
    handler.run()


# Функция для запуска слушателя RabbitMQ в отдельном потоке
def run_rabbit_listener():
    init_rabbit_producer(
        host=config.RABBIT_HOST,
        input_queue=config.GATEWAY_INPUT_QUEUE,
        cb_queue=config.CALLBACK_SERV_QUEUE,
        password=config.RABBIT_PASSWORD,
        username=config.RABBIT_USER,
    )
    rabbit_producer.start_listening()


async def main():
    logging.basicConfig(level=logging.INFO)

    with ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()

        # Передаем порт в run_http_server через partial
        run_http_server_partial = partial(run_http_server, config.SERVER_PORT)
        run_rabbit_partial = partial(run_rabbit_listener)

        # Запуск HTTP сервера и RabbitMQ listener параллельно
        await asyncio.gather(
            loop.run_in_executor(executor, run_rabbit_partial),
            loop.run_in_executor(executor, run_http_server_partial)
        )


if __name__ == "__main__":
    asyncio.run(main())