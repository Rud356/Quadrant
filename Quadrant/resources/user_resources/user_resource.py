from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.exc import NoResultFound

from Quadrant.models.users_package import User
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import HTTPError, user_schemas
from .router import router


@router.get(
    "/api/v1/users/me",
    description="Gives information about authorized user.",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["User information"]
)
async def get_user_info_about_authorized(request: Request):
    return request.state["authorized_user"].user.as_dict()


@router.get(
    "/api/v1/users/find",
    description="Gives information about user by his color id and username.",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["User information"]
)
async def find_user_by_username_and_color_id(search_parameters: user_schemas.SearchUserBody, request: Request):
    sql_session = request.state["sql_session"]

    try:
        user = await User.get_user_by_username_and_color_id(
            search_parameters.username, search_parameters.color_id, session=sql_session
        )

    except (NoResultFound, OverflowError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": "NOT_FOUND",
                "message": "User with given parameters not found",
                "parameters": {"username": search_parameters.username, "color_id": search_parameters.color_id}
            }
        )

    return user.as_dict()


@router.get(
    "/api/v1/users/{user_id}",
    description="Gives information about user.",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["User information"]
)
async def get_user_info_about(user_id: UUID, request: Request):
    sql_session = request.state["sql_session"]
    try:
        user = await User.get_user(user_id, session=sql_session)

    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": "NOT_FOUND", "message": "User with given id not found"}
        )

    return user.as_dict()
