from fastapi import Depends, Request, status
from fastapi.responses import ORJSONResponse

from Quadrant.models.users_package import UserSession
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import HTTPError, session_schema
from .router import router


@router.get(
    "/api/v1/sessions/{session_id}",
    description="Gives information about current session",
    responses={
        200: {"model": session_schema.SessionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
async def get_current_session_info(session_id: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        session: UserSession = await UserSession.get_alive_user_session(
            db_user.id, session_id, session=sql_session
        )
        session_data = session.as_dict()

    except ValueError:
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"reason": "INVALID_SESSION_ID", "message": "No session with that id found"}
        )

    return ORJSONResponse(
        content=session_data,
        status_code=status.HTTP_200_OK
    )


@router.delete(
    "/api/v1/sessions/{session_id}",
    description="Terminates one exact session",
    responses={
        200: {"model": session_schema.TerminatedSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError},
    },
    dependencies=[Depends(require_authorization, use_cache=False)],
    tags=["Users session management"]
)
@require_authorization
async def get_current_session_info(session_id: int, request: Request):
    db_user = request.scope["db_user"]
    sql_session = request.scope["sql_session"]

    try:
        session: UserSession = await UserSession.get_alive_user_session(
            db_user.id, session_id, session=sql_session
        )

    except ValueError:
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"reason": "INVALID_SESSION_ID", "message": "No session with that id found"}
        )

    await session.terminate_session(session=sql_session)

    return ORJSONResponse(
        content={"session_id": session_id, "successfully_terminated": True},
        status_code=status.HTTP_200_OK
    )
