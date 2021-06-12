from fastapi import Request

from Quadrant.quadrant_app import app
from Quadrant.models.db_init import Session


@app.middleware("http")
async def get_sqlalchemy_session(request: Request, call_next):
    async with Session() as session:
        request.sql_session = session
        response = await call_next(request)

    return response
