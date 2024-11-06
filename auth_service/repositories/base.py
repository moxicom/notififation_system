from tortoise import Tortoise
import os
import logging

log = logging.getLogger(__name__)

USER = os.getenv('POSTGRES_USER', default='myuser')
PASSWORD = os.getenv('POSTGRES_PASSWORD', default='mypassword')
DB = os.getenv('POSTGRES_DB', default='mydatabase')
DB_HOST = os.getenv('DB_HOST', default='localhost:5432')

env_vars = os.environ

async def init():
    try:
        await Tortoise.init(
            db_url=f'postgres://{USER}:{PASSWORD}@{DB_HOST}/{DB}',
            modules={'models': ['models']} # models: package (or models.user)
        )
    except Exception as e:
        log.error(f"failed to init db. {e}")
        raise SystemExit(1)
    log.info("connected to database")
    try:
        await Tortoise.generate_schemas()
    except Exception as e:
        log.error(f"failed to generate schemas {e}")
        raise SystemExit(1)


# async def run():
#     await init()
#
#     user = await User.create(username="johndoe", email="john@example.com")
#
#     users = await User.all()
#     print(users)


# run_async(run())

async def close():
    await Tortoise.close_connections()