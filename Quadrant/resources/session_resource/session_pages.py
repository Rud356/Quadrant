from fastapi import status
from fastapi.responses import ORJSONResponse

from Quadrant.middlewares.custom_objects import RequestWithAuthorizedUser
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
    }
)
@require_authorization
async def get_pages_count(request: RequestWithAuthorizedUser):
    pages = UserSession.get_sessions_pages_count(user_id=request.user.id, session=request.sql_session)

    return {"pages": pages}


@router.get(
    "/api/v1/sessions/pages/{page}",
    responses={
        200: {"model": session_schema.SessionsPageSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
    }
)
async def get_session_page(page: int, request: RequestWithAuthorizedUser):
    try:
        sessions_page = await UserSession.get_user_sessions_page(
            request.user.id, page, session=request.sql_session
        )

    except ValueError:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"reason": "INVALID_PAGE", "message": "You've tried to access invalid sessions page"}
        )

    return {"sessions": [session.as_dict() for session in sessions_page]}
