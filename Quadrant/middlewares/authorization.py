from enum import Enum, auto

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import NoResultFound

from Quadrant.models import users_package
from .custom_objects import RequestWithSession


class UserType(Enum):
    Bot = auto()
    Bearer = auto()


async def user_authorization(request: RequestWithSession, call_next):
    # TODO: add JWT
    token = request.headers.get("token") or request.cookies.get("token")
    session_id = request.cookies.get("session")

    if token is not None and session_id is not None:
        token_type, _, token = token.partition(" ")

        try:
            token_type = UserType[token_type]

        except KeyError:
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"reason": "INVALID_TOKEN_TYPE", "message": "No such token owner type"}
            )

        try:
            authorized_user = await users_package.UserInternalAuthorization.authorize_with_token(
                token, token_type == UserType.Bot, session=request.sql_session
            )

        except NoResultFound:
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"reason": "INVALID_TOKEN", "message": "You've provided invalid token"}
            )

        try:
            session_id = int(session_id)
            user_session = await users_package.UserSession.get_alive_user_session(
                authorized_user.user_id, session_id=session_id, session=request.sql_session
            )

        except ValueError:
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"reason": "INVALID_SESSION", "message": "Your session is invalid"}
            )

        request.scope['user'] = authorized_user.user
        request.authorized_user = authorized_user
        request.user_session = user_session

    else:
        request.authorized_user = None
        request.user_session = None

    return await call_next(request)
