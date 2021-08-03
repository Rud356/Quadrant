from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import exc

from Quadrant.models import users_package
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, http_error_example, relations_schema
from .router import router


@router.get(
    "/api/v1/relations/blocked/pages",
    description="Gives a number of pages with blocked users (pages starting from 1).",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationsPagesCount},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError}
    },
    tags=["Users relationships", "Blocked relation"]
)
async def get_blocked_pages_count(request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    pages = await users_package.UserRelation.get_relations_pages_count(
        db_user, users_package.UsersRelationType.blocked,
        session=sql_session
    )

    return relations_schema.RelationsPagesCount.construct(
        relation_type=users_package.UsersRelationType.blocked,
        pages=pages
    )


@router.get(
    "/api/v1/relations/blocked/pages/{page}",
    description="Gives a page of block list (pages starting from 1).",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RelationsPage},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example("INVALID_PAGE", "No content to show")
        },
    },
    tags=["Users relationships", "Blocked relation"]
)
async def get_blocked_page(page: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    # We want to have pages from 1, but offset should start from 0
    page -= 1
    try:
        relations_page = await users_package.UserRelation.get_relations_page(
            db_user.id, users_package.UsersRelationType.blocked,
            page, session=sql_session
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_PAGE", "message": "No content to show"}
        )

    return relations_page


@router.patch(
    "/api/v1/relations/blocked/{user_id}",
    description="Adds user to block list.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.BlockedNotification},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example("INVALID_BLOCKED_USER", "User is in your block list")
        },
        status.HTTP_404_NOT_FOUND: {
            "model": http_error_example("USER_NOT_FOUND", "User with given id not found")
        }
    },
    tags=["Users relationships", "Blocked relation"]
)
async def block_user(user_id: UUID, request: Request):
    # TODO: send notification about blocking user to receiver and new blocked user
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        user = await users_package.User.get_user(user_id, session=sql_session)
        await users_package.UserRelation.block_user(
            db_user, user, session=sql_session
        )

    except exc.NoResultFound:
        raise HTTPException(
            status_code=404,
            detail={"reason": "USER_NOT_FOUND", "message": "User with given id not found"}
        )

    except users_package.UserRelation.exc.AlreadyBlockedException:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_BLOCKED_USER", "message": "User is in your block list"}
        )

    return {"blocked_user_id": user_id}


@router.delete(
    "/api/v1/relations/blocked/{user_id}",
    description="Deletes user from block list.",
    dependencies=[Depends(require_authorization, use_cache=False)],
    responses={
        200: {"model": relations_schema.RemovedFromBlockNotification},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example("INVALID_BLOCKED_USER", "User isn't in your block list"),
        },
    },
    tags=["Users relationships", "Blocked relation"]
)
async def unblock_user(user_id: UUID, request: Request):
    # TODO: send notification about unblocking user on all devices requester is
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        blocked_relation = await users_package.UserRelation.get_relationship(
            db_user, user_id, session=sql_session
        )
        await blocked_relation.unblock_user(session=sql_session)

    except exc.NoResultFound:
        raise HTTPException(
            status_code=400,
            detail={"reason": "INVALID_BLOCKED_USER", "message": "User isn't in your block list"}
        )

    return {"unblocked_user_id": user_id}
