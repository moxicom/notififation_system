import logging

import uvicorn
from fastapi import FastAPI
from adapters.httpserver import router

LOGGER = logging.getLogger(__name__)



class HttpHandler:
    def __init__(self, port: int, http_router: FastAPI):
        self.port: int = port
        self.handler: FastAPI = http_router

    def run(self):
        uvicorn.run(self.handler, host="0.0.0.0" ,port=self.port)

def create_rest_handler(port: int) -> HttpHandler:
    fast_api = FastAPI(
        title="Callback API",
        description="api for callbacks from senders",
        version="1.0.0",
    )

    fast_api.include_router(router, prefix="/api/v1")

    LOGGER.info("created handler")

    http_handler = HttpHandler(port, fast_api)

    return http_handler