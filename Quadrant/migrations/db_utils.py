from Quadrant.models import db_init
from Tests.utils import make_async_call
from Quadrant.models import users_package, dm_channel_package, group_channel_package  # noqa: inits models
from Quadrant.config import quadrant_config

metadata = db_init.Base.metadata


@make_async_call
async def initialize_db():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@make_async_call
async def drop_db():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
