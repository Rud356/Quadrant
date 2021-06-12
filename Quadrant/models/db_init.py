from functools import wraps

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from Quadrant.config import quadrant_config
from Quadrant.quadrant_logging import app_log

Base = declarative_base()
Session = sessionmaker(
    quadrant_config.DBConfig.async_base_engine,
    expire_on_commit=False, class_=AsyncSession,
)


def async_session(f):
    @wraps(f)
    async def grab_session(*args, **kwargs):
        async with Session() as session:
            try:
                return await f(*args, **kwargs, session=session)

            except IntegrityError as err:
                await session.rollback()
                app_log.exception(err)

    return grab_session
