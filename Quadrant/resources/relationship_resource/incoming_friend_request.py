from uuid import UUID

from typing import Optional
from fastapi import Depends, Request, status, HTTPException
from sqlalchemy import exc

from .router import router
from Quadrant.resources.utils import require_authorization
from Quadrant.models import users_package
from Quadrant.schemas import HTTPError, relations_schema


@router.get(
    "/api/v1/relations/incoming_friend_requests/pages/{page}",
    description="Gives a page of incoming friend requests (pages starting from 1).",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationsPage},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
    },
    tags=["Users relationships", "Incoming friend request relation"]
)
async def get_incoming_friend_requests_page(page: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    # We want to have pages from 1, but offset should start from 0
    page -= 1
    try:
        relations_page = await users_package.UsersRelations.get_relationships_page(
            db_user.id, page, users_package.UsersRelationType.friend_request_receiver, session=sql_session
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_PAGE", "message": "No content to show"}
        )

    return {"relations": relations_page}


@router.patch(
    "/api/v1/relations/incoming_friend_requests/{to_user_id}",
    description="Accepts friend request from this user or denies it.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.ResponseOnIncomingFriendRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    },
    tags=["Users relationships", "Incoming friend request relation"]
)
async def respond_on_incoming_friend_request(from_user_id: UUID, request: Request, accept: Optional[bool] = True):
    # TODO: send notification about responding on friend request to sender devices and to whom we responded
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        user = await users_package.User.get_user(from_user_id, session=sql_session)
        await users_package.UsersRelations.respond_on_friend_request(
            db_user, user, accept_request=accept, session=sql_session
        )

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "NO_USER_FOUND", "message": "No user found"}
        )

    except users_package.UsersRelations.exc.RelationshipsException:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_RELATION", "message": "User didn't sent you friend request"}
        )

    return {"response_to": from_user_id, "accepted_request": accept}


@router.delete(
    "/api/v1/relations/incoming_friend_requests/{with_user_id}",
    description="Denies friend request.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.ResponseOnIncomingFriendRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    },
    tags=["Users relationships", "Incoming friend request relation"]
)
async def deny_incoming_friend_request(from_user_id: UUID, request: Request):
    # TODO: send notification about responding on friend request to sender devices and to whom we responded
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        user = await users_package.User.get_user(from_user_id, session=sql_session)
        await users_package.UsersRelations.respond_on_friend_request(
            db_user, user, accept_request=False, session=sql_session
        )

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "NO_USER_FOUND", "message": "No user found"}
        )

    except users_package.UsersRelations.exc.RelationshipsException:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_RELATION", "message": "User didn't sent you friend request"}
        )

    return {"response_to": from_user_id, "accepted_request": False}
