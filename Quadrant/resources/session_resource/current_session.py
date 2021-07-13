from fastapi import Depends, Request, status

from Quadrant.models.users_package import UserSession
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import UNAUTHORIZED_HTTPError, session_schema
from .router import router


@router.get(
    "/api/v1/sessions/current",
    description="Gives information about current session",
    responses={
        200: {"model": session_schema.SessionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
async def get_current_session_info(request: Request):
    user_session: UserSession = request.scope["user_session"]
    session_data = user_session.as_dict()

    return session_data


@router.delete(
    "/api/v1/sessions/current",
    description="Terminates current session",
    responses={
        200: {"model": session_schema.TerminatedSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": UNAUTHORIZED_HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
async def get_current_session_info(request: Request):
    sql_session = request.scope["sql_session"]
    user_session: UserSession = request.scope["user_session"]
    session_id: UserSession.session_id = user_session.session_id

    await user_session.terminate_session(session=sql_session)

    return {"session_id": session_id, "successfully_terminated": True}
