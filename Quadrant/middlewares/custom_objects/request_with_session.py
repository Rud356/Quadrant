from fastapi import Request

from sqlalchemy.ext.asyncio import AsyncSession


class RequestWithSession(Request):
    sql_session: AsyncSession
