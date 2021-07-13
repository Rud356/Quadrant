from fastapi import Depends, HTTPException, Request, status

from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, http_error_example, user_schemas
from .router import router


@router.get(
    "/api/v1/profile/status",
    description="Gives information about current users status.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": user_schemas.UserProfilePart},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
    tags=["User profile management"]
)
async def get_requester_status(request: Request):
    db_user: users_package.User = request.scope["db_user"]
    return {"part_name": "status", "value": db_user.status}


@router.patch(
    "/api/v1/profile/status",
    description="Sets new users status.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": user_schemas.UserProfilePart},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "INVALID_STATUS", "You've sent invalid user status."
            )
        },
    },
    tags=["User profile management"]
)
async def set_requester_status(new_status: str, request: Request):
    # TODO: send notification about it being updated
    db_user: users_package.User = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        await db_user.set_status(new_status, session=sql_session)

    except KeyError:
        raise HTTPException(status_code=400, detail={
            "reason": "INVALID_STATUS",
            "message": "You've sent invalid user status."
        })

    return {"part_name": "status", "value": db_user.status}
