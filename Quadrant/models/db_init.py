from functools import wraps
from tornado.log import app_log
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from Quadrant.config import quadrant_config

Base = declarative_base()
Session = sessionmaker(quadrant_config.DBConfig.async_engine, expire_on_commit=False, class_=AsyncSession)


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
