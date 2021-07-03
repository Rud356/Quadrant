import asyncio

from Quadrant.config import quadrant_config
from Quadrant import models
from Quadrant.models import (
    users_package, dm_channel_package, group_channel_package,
    servers_package
)

Base = models.Base


async def init_db_tables():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Created tables")

loop = asyncio.get_event_loop()
loop.run_until_complete(init_db_tables())
