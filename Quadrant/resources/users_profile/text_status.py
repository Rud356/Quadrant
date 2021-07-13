from fastapi import Depends, HTTPException, Request, status

from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, http_error_example, user_schemas
from .router import router


@router.get(
    "/api/v1/profile/text_status",
    description="Gives information about current users text status.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": user_schemas.UserProfilePart},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
    tags=["User profile management"]
)
async def get_requester_text_status(request: Request):
    db_user: users_package.User = request.scope["db_user"]
    return {"part_name": "text_status", "value": db_user.text_status}


@router.patch(
    "/api/v1/profile/text_status",
    description="Sets new text status.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": user_schemas.UserProfilePart},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "INVALID_TEXT_STATUS",
                "You've sent invalid text status that didn't matched requirements."
            )
        },
    },
    tags=["User profile management"]
)
async def set_requester_text_status(new_status: str, request: Request):
    # TODO: send notification about it being updated
    db_user: users_package.User = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        await db_user.set_text_status(new_status, session=sql_session)

    except ValueError:
        raise HTTPException(status_code=400, detail={
            "reason": "INVALID_TEXT_STATUS",
            "message": "You've sent invalid text status that didn't matched requirements."
        })

    return {"part_name": "text_status", "value": db_user.text_status}
