import logging
from cgitb import reset
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter

from adapters.httpserver.router import router
from adapters.rabbithandler import RabbitMQProducer

fastapi_logger = logging.getLogger(__name__)

class HttpHandler:
    def __init__(self, port: int, http_router: FastAPI):
        self.port: int = port
        self.handler: FastAPI = http_router

    def run(self):
        uvicorn.run(self.handler, host="0.0.0.0" ,port=self.port)



# def init_http_server() -> FastAPI:
@asynccontextmanager
async def lifespan(app: FastAPI):
    fastapi_logger.info("Starting fast api")
    yield
    fastapi_logger.info("Shutting down fast api")


def create_rest_handler(port: int) -> HttpHandler:
    fast_api = FastAPI(
        title="GATEWAY API",
        description="This API allows to use system by http (and rabbit btw)",
        version="1.0.0",
        lifespan=lifespan
    )

    fast_api.include_router(router, prefix="/api/v1")

    fastapi_logger.info("created handler")

    http_handler = HttpHandler(port, fast_api)

    return http_handler