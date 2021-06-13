from fastapi import Depends, Request, status
from fastapi.responses import ORJSONResponse

from Quadrant.models.users_package import UserSession
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import HTTPError, session_schema
from .router import router


@router.get(
    "/api/v1/sessions/pages",
    description="Gives number of pages with sessions history",
    responses={
        200: {"model": session_schema.SessionPagesCountSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
async def get_pages_count(request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    pages = UserSession.get_sessions_pages_count(
        user_id=db_user.id, session=sql_session
    )

    return {"pages": pages}


@router.get(
    "/api/v1/sessions/pages/{page}",
    responses={
        200: {"model": session_schema.SessionsPageSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
async def get_session_page(page: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        sessions_page = await UserSession.get_user_sessions_page(
            db_user.id, page, session=sql_session
        )

    except ValueError:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"reason": "INVALID_PAGE", "message": "You've tried to access invalid sessions page"}
        )

    return {"sessions": [session.as_dict() for session in sessions_page]}
