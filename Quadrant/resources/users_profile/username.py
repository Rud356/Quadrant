from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError

from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, http_error_example, user_schemas
from .router import router


@router.get(
    "/api/v1/profile/username",
    description="Gives information about current users username.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": user_schemas.UserProfilePart},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
)
async def get_requester_username(request: Request):
    db_user: users_package.User = request.scope["db_user"]
    return {"part_name": "username", "value": db_user.username}


@router.patch(
    "/api/v1/profile/username",
    description="Sets new username.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": user_schemas.UserProfilePart},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "INVALID_USERNAME", "This combination of username and color id is already in use."
            )
        },
    },
)
async def set_requester_username(new_username: user_schemas.UserSchema.username, request: Request):
    # TODO: send notification about it being updated
    db_user: users_package.User = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        await db_user.set_username(new_username, session=sql_session)

    except IntegrityError:
        raise HTTPException(status_code=400, detail={
            "reason": "INVALID_USERNAME",
            "message": "This combination of username and color id is already in use."
        })

    return {"part_name": "username", "value": db_user.username}
