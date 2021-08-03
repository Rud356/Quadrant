from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import exc

from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, http_error_example, relations_schema
from Quadrant.schemas.user_schemas import SearchUserBody
from .router import router


@router.get(
    "/api/v1/relations/outgoing_friend_requests/pages",
    description="Gives a number of pages with users that received your friend requests (pages starting from 1).",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationsPagesCount},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError}
    },
    tags=["Users relationships", "Incoming friend request relation"]
)
async def get_incoming_friend_requests_pages_count(request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    pages = await users_package.UserRelation.get_relations_pages_count(
        db_user, users_package.UsersRelationType.friend_request_receiver,
        session=sql_session
    )

    return relations_schema.RelationsPagesCount.construct(
        relation_type=users_package.UsersRelationType.friend_request_receiver,
        pages=pages
    )


@router.get(
    "/api/v1/relations/outgoing_friend_requests/pages/{page}",
    description="Gives a page of outgoing friend requests (pages starting from 1).",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationsPage},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": http_error_example("INVALID_PAGE", "No content to show")},
    },
    tags=["Users relationships", "Outgoing friend request relation"]
)
async def get_outgoing_friend_requests_page(page: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    # We want to have pages from 1, but offset should start from 0
    page -= 1
    try:
        relations_page = await users_package.UserRelation.get_relations_page(
            db_user.id, users_package.UsersRelationType.friend_request_sender,
            page, session=sql_session
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_PAGE", "message": "No content to show"}
        )

    return relations_page


@router.patch(
    "/api/v1/relations/outgoing_friend_requests/with_user_tag",
    description="Sends friend request using users tag.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.FriendRequestSent},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "IN_RELATIONS_WITH_USER", "You already have some relations with this user"
            )
        },
        status.HTTP_404_NOT_FOUND: {
            "model": http_error_example(
                "USER_NOT_FOUND", "User with given id not found"
            )
        }
    },
    tags=["Users relationships", "Outgoing friend request relation"]
)
async def send_friend_request_by_user_tag(user_tag: SearchUserBody, request: Request):
    # TODO: add check if user wants to accept any friend requests
    # TODO: send notification about new friend request to receiver and to all sender devices
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        user = await users_package.User.get_user_by_username_and_color_id(
            user_tag.username, user_tag.color_id, session=sql_session
        )
        await users_package.UserRelation.send_friend_request(
            db_user, user, session=sql_session
        )

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "USER_NOT_FOUND", "message": "User with given id not found"}
        )

    except users_package.UserRelation.exc.AlreadyHasRelationshipException:
        raise HTTPException(
            status_code=400,
            detail={
                "reason": "IN_RELATIONS_WITH_USER",
                "message": "You already have some relations with this user"
            }
        )

    return {"friend_request_receiver_id": user.id}


@router.patch(
    "/api/v1/relations/outgoing_friend_requests/{to_user}",
    description="Sends friend request.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.FriendRequestSent},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "IN_RELATIONS_WITH_USER", "You already have some relations with this user"
            )
        },
        status.HTTP_404_NOT_FOUND: {
            "model": http_error_example(
                "USER_NOT_FOUND", "User with given id not found"
            )
        }
    },
    tags=["Users relationships", "Outgoing friend request relation"]
)
async def send_friend_request(to_user_id: UUID, request: Request):
    # TODO: add customization of who can send requests to whom
    # TODO: send notification about new friend request to receiver and to all sender devices
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        user = await users_package.User.get_user(to_user_id, session=sql_session)
        await users_package.UserRelation.send_friend_request(
            db_user, user, session=sql_session
        )

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "USER_NOT_FOUND", "message": "User with given id not found"}
        )

    except users_package.UserRelation.exc.AlreadyHasRelationshipException:
        # TODO: handle case when user is trying to send friend request to himself
        raise HTTPException(
            status_code=400,
            detail={
                "reason": "IN_RELATIONS_WITH_USER",
                "message": "You already have some relations with this user"
            }
        )

    return {"friend_request_receiver_id": to_user_id}


@router.delete(
    "/api/v1/relations/outgoing_friend_requests/{to_user}",
    description="Cancels sent friend request.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.CancelledFriendRequest},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "NO_OUTGOING_REQUEST", "You already have some relations with this user"
            )
        },
        status.HTTP_404_NOT_FOUND: {
            "model": http_error_example(
                "USER_NOT_FOUND", "User with given id not found"
            )
        },
    },
    tags=["Users relationships", "Outgoing friend request relation"]
)
async def cancel_friend_request(to_user_id: UUID, request: Request):
    # TODO: send notification about cancelled friend request to receiver and to all sender devices
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        relation_with_user = await users_package.UserRelation.get_relationship(
            db_user, to_user_id, session=sql_session
        )
        await relation_with_user.cancel_friend_request(session=sql_session)

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "USER_NOT_FOUND", "message": "User with given id not found"}
        )

    except users_package.UserRelation.exc.InvalidRelationshipStatusException:
        raise HTTPException(
            status_code=400,
            detail={
                "reason": "NO_OUTGOING_REQUEST",
                "message": "You did not sent friend request to this user"
            }
        )

    return {"friend_request_receiver_id": to_user_id, "friend_request_sender_id": db_user.id}
