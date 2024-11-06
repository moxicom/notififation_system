import uvicorn
from fastapi import FastAPI
import logging

from api.v1.routes import router
from core.logging import setup_logging
from repositories.base import init as init_db, close as close_db
from contextlib import asynccontextmanager

setup_logging(debug=False)

log = logging.getLogger(__name__)
fastapi_logger = logging.getLogger("fastapi")

@asynccontextmanager
async def lifespan(app: FastAPI):
    fastapi_logger.info("Initializing database...")
    await init_db()
    fastapi_logger.info("Database initialized")

    yield

    fastapi_logger.info("Closing database connections...")
    await close_db()
    fastapi_logger.info("Database connections closed")


def create_rest_handler() -> FastAPI:
    handler = FastAPI(
        title="Auth Service API",
        description="This API allows you to register users and obtain JWT tokens.",
        version="1.0.0",
        lifespan=lifespan
    )
    handler.include_router(router, prefix="/api/v1")
    log.info("created handler")
    return handler


app = create_rest_handler()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Auth Service")
    # parser.add_argument('-d', action='store_true', help='Enable debug logging')
    # args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=8000)
