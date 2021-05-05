from Quadrant.config import quadrant_config
from Quadrant.models import db_init, dm_channel_package, group_channel_package, users_package  # noqa: inits models
from tests.utils import make_async_call

metadata = db_init.Base.metadata


@make_async_call
async def initialize_db():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


@make_async_call
async def drop_db():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
