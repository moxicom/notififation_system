import argparse
import asyncio
import uvicorn
from fastapi import FastAPI
import logging

from api.v1.routes import router
from core.logging import setup_logging
from tortoise import Tortoise
from repositories.base import init as init_db, close as close_db

log = logging.getLogger(__name__)


def create_rest_handler() -> FastAPI:
    handler = FastAPI(
        title="Auth Service API",
        description="This API allows you to register users and obtain JWT tokens.",
        version="1.0.0"
    )
    handler.include_router(router, prefix="/api/v1")
    log.info("created handler")
    return handler

app = create_rest_handler()

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auth Service")
    parser.add_argument('-d', action='store_true', help='Enable debug logging')
    args = parser.parse_args()

    setup_logging(debug=args.d)

    uvicorn.run(app, host="0.0.0.0", port=8000)
