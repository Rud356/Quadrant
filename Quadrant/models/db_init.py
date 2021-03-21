from functools import wraps

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from Quadrant.config import quadrant_config

Base = declarative_base()
Session = sessionmaker(quadrant_config.DBConfig.async_engine, expire_on_commit=False, class_=AsyncSession)


async def async_session(f):
    @wraps(f)
    async def grab_session(*args, **kwargs):
        async with Session() as session:
            return await f(*args, **kwargs, session=session)
    return grab_session

