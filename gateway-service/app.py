import asyncio
import logging
from asyncio import get_running_loop
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from adapters.httpserver import create_rest_handler
from adapters.rabbithandler.rabbit import rabbit_producer

# from adapters.rabbithandler import init_rabbit_producer, rabbit_producer
from core.config import config


# Функция для запуска HTTP сервера
def run_http_server_sync(port: int):
    handler = create_rest_handler(port)
    handler.run()

async def run_http_server(port):
    loop = get_running_loop()
    with ThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, run_http_server_sync, port)

async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        await asyncio.gather(
            rabbit_producer.consume(),
            run_http_server(8000)
        )
    except Exception as e:
        logging.exception("Application failed to start.")
        raise SystemExit(1)
    finally:
        logging.info("Shutting down application.")

if __name__ == "__main__":
    # Use asyncio.run() if not in a running event loop
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called" in str(e):
            # For environments with a running event loop
            logging.warning("Running inside an already started event loop.")
            asyncio.create_task(main())
        else:
            raise
