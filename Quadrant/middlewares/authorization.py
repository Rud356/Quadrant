from contextlib import suppress
from enum import Enum, auto

import jwt
from fastapi import HTTPException, Request, status
from sqlalchemy.exc import NoResultFound

from Quadrant.config import quadrant_config
from Quadrant.models import users_package
from Quadrant.quadrant_logging import app_log


class UserType(Enum):
    Bot = auto()
    Bearer = auto()


async def user_authorization(request: Request, call_next):
    session_token = request.cookies.get("session_token") or request.headers.get("session_token")

    if session_token is None:
        request.scope["db_user"] = None
        request.scope["authorized_user"] = None
        request.scope["user_session"] = None
        app_log.debug("No session token provided")

    else:
        sql_session = request.scope['sql_session']
        token_type, _, session_token = session_token.partition(" ")

        with suppress(jwt.DecodeError):
            session_dict = jwt.decode(
                session_token,
                quadrant_config.Security.cookie_secret.value,
                algorithm="HS256", require=["exp", "session_id", "token"]
            )
            token = session_dict.get('token')
            session_id = session_dict.get('session_id')

        app_log.debug(f"User token and session id -> {token} {session_id}")
        if token is not None and session_id is not None:
            try:
                token_type = UserType[token_type]
                app_log.debug(f"User token type -> {token_type}")

            except KeyError:
                app_log.debug(f"User provided invalid user token type -> {token_type}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"reason": "INVALID_TOKEN_TYPE", "message": "No such token owner type"}
                )

            try:
                authorized_user = await users_package.UserInternalAuthorization.authorize_with_token(
                    token, token_type == UserType.Bot, session=sql_session
                )
                app_log.debug(f"Authorized as user with id -> {authorized_user.user_id}")

            except NoResultFound:
                app_log.warn(f"Invalid user token -> {token_type} {token} from {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"reason": "INVALID_TOKEN", "message": "You've provided invalid token"}
                )

            try:
                session_id = int(session_id)
                user_session: users_package.UserSession = await users_package.UserSession.get_alive_user_session(
                    authorized_user.user_id, session_id=session_id, session=sql_session
                )
                app_log.info(f"Authorized user {user_session.user_id} on session {user_session.session_id}")

            except ValueError:
                app_log.warn(
                    f"Invalid user session for user {authorized_user.user_id}"
                    f" -> {session_id} from {request.client.host}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"reason": "INVALID_SESSION", "message": "Your session is invalid"}
                )

            request.scope["db_user"] = authorized_user.user
            request.scope["authorized_user"] = authorized_user
            request.scope["user_session"] = user_session

    return await call_next(request)
