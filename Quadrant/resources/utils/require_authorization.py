from functools import wraps
from fastapi import status
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from Quadrant.middlewares.custom_objects import RequestWithAuthorizedUser


def require_authorization(f):
    @wraps(f)
    async def wrapper(*args, request: Request, **kwargs):
        request: RequestWithAuthorizedUser
        if not hasattr(request, "authorized_user"):
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"reason": "UNAUTHORIZED", "message": "You aren't authorized to access this resource"}
            )

        return await f(*args, **kwargs, request=request)
    return wrapper
