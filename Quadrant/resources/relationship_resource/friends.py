from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import exc

from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, http_error_example, relations_schema
from .router import router


@router.get(
    "/api/v1/relations/friends/pages/{page}",
    description="Gives a page of friends (pages starting from 1).",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationsPage},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": http_error_example("INVALID_PAGE", "No content to show")},
    },
    tags=["Users relationships", "Friends relation"]
)
async def get_friends_page(page: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    # We want to have pages from 1, but offset should start from 0
    page -= 1
    try:
        relations_page = await users_package.UsersRelations.get_relationships_page(
            db_user.id, page, users_package.UsersRelationType.friends, session=sql_session
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_PAGE", "message": "No content to show"}
        )

    return {"relations": relations_page}


@router.delete(
    "/api/v1/relations/friends/{with_user_id}",
    description="Deletes user from friends.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.UnfriendedUserNotification},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example("INVALID_FRIEND_USER", "User isn't your friend")
        },
        status.HTTP_404_NOT_FOUND: {
            "model": http_error_example("USER_NOT_FOUND", "User with given id not found")
        }
    },
    tags=["Users relationships", "Friends relation"]
)
async def delete_friend(with_user_id: UUID, request: Request):
    # TODO: send notification about unfriending

    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        friend = await users_package.User.get_user(with_user_id, session=sql_session)
        await users_package.UsersRelations.remove_user_from_friends(
            db_user, friend, session=sql_session
        )

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "USER_NOT_FOUND", "message": "User with given id not found"}
        )

    except users_package.UsersRelations.exc.RelationshipsException:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_FRIEND_USER", "message": "User isn't your friend"}
        )

    return {"unfriended_user_id": with_user_id}
