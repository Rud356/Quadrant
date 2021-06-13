from fastapi import Request

from Quadrant.models.db_init import Session


async def get_sqlalchemy_session(request: Request, call_next):
    if hasattr(request, "sql_session"):
        return await call_next(request)

    async with Session() as session:
        request.scope["sql_session"] = session
        response = await call_next(request)

    return response
