from fastapi import Request, status
from fastapi.exceptions import HTTPException


def require_authorization(request: Request):
    if not request.scope.get("db_user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"reason": "UNAUTHORIZED", "message": "You aren't authorized to access this resource"}
        )
