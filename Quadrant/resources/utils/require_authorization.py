from fastapi import status
from fastapi.exceptions import HTTPException

from Quadrant.middlewares.custom_objects import RequestWithAuthorizedUser


def require_authorization(request: RequestWithAuthorizedUser):
    if not hasattr(request, "authorized_user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"reason": "UNAUTHORIZED", "message": "You aren't authorized to access this resource"}
        )
