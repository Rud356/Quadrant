from typing import Optional, Tuple

from sqlalchemy import exc
from tornado.web import RequestHandler

from Quadrant.models.users_package import UserInternalAuthorization, UserSession


async def authorization_middleware(
    request_context: RequestHandler, session
) -> Tuple[Optional[UserInternalAuthorization], Optional[UserSession]]:
    token = request_context.get_secure_cookie("token") or request_context.request.headers.get("token")

    if token is None:
        return None, None

    try:
        token = str(token)
        token_type, token = token.split(' ', 1)

    except ValueError:
        return None, None

    if token_type == "Bearer":
        is_bot = False
    elif token_type == "Bot":
        is_bot = True
    else:
        # Not supported token type
        return None, None

    try:
        auth_user = await UserInternalAuthorization.authorize_with_token(token, is_bot, session=session)
        session_id = request_context.get_secure_cookie("session_id")
        session_id = int(str(session_id))

        user_session = UserSession.get_user_session(
            auth_user.user_id, session_id=session_id, session=session
        )

    except (exc.NoResultFound, ValueError):
        auth_user = None
        user_session = None

    return auth_user, user_session
