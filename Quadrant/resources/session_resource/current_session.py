from fastapi import status
from fastapi.responses import ORJSONResponse

from Quadrant.middlewares.custom_objects import RequestWithAuthorizedUser
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import HTTPError, session_schema
from .router import router


@router.get(
    "/api/v1/sessions/current",
    description="Gives information about current session",
    responses={
        200: {"model": session_schema.SessionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
    }
)
@require_authorization
async def get_current_session_info(request: RequestWithAuthorizedUser):
    session_data = request.user_session.as_dict()
    return ORJSONResponse(
        content=session_data,
        status_code=status.HTTP_200_OK
    )


@router.delete(
    "/api/v1/sessions/current",
    description="Terminates current session",
    responses={
        200: {"model": session_schema.TerminatedSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
    }
)
@require_authorization
async def get_current_session_info(request: RequestWithAuthorizedUser):
    session_id = request.user_session.session_id
    await request.user_session.terminate_session(session=request.sql_session)

    return ORJSONResponse(
        content={"session_id": session_id, "successfully_terminated": True},
        status_code=status.HTTP_200_OK
    )
