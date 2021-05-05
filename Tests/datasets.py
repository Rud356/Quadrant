from Quadrant.models import users_package
from Quadrant.config import quadrant_config
from Quadrant.migrations import db_utils


async def create_user(
    username: str, login: str, password: str, session
) -> users_package.user_auth.UserInternalAuthorization:
    return await users_package.user_auth.UserInternalAuthorization.register_user_internally(
        username, login, password, session=session
    )


async def async_init_db():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(db_utils.metadata.create_all)


async def async_drop_db():
    async with quadrant_config.DBConfig.async_base_engine.begin() as conn:
        await conn.run_sync(db_utils.metadata.drop_all)
