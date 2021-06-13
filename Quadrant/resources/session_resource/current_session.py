from fastapi import Depends, Request, status
from fastapi.responses import ORJSONResponse

from Quadrant.resources.utils import require_authorization
from Quadrant.models.users_package import UserSession
from Quadrant.schemas import HTTPError, session_schema
from .router import router


@router.get(
    "/api/v1/sessions/current",
    description="Gives information about current session",
    responses={
        200: {"model": session_schema.SessionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
@require_authorization
async def get_current_session_info(request: Request):
    user_session: UserSession = request.scope["user_session"]
    session_data = user_session.as_dict()

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
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
@require_authorization
async def get_current_session_info(request: Request):
    sql_session = request.scope["sql_session"]
    user_session: UserSession = request.scope["user_session"]
    session_id: UserSession.session_id = user_session.session_id

    await user_session.terminate_session(session=sql_session)

    return ORJSONResponse(
        content={"session_id": session_id, "successfully_terminated": True},
        status_code=status.HTTP_200_OK
    )
