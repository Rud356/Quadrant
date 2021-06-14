from datetime import datetime, timedelta

import jwt
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from Quadrant.config import quadrant_config
from Quadrant.models.users_package import UserInternalAuthorization, UserSession


async def prepare_users_client_authorization(
    new_authorized_user: UserInternalAuthorization, sql_session: AsyncSession,
    request: Request, response: Response
) -> None:
    new_session = await UserSession.new_session(
        new_authorized_user.user, request.client.host, session=sql_session
    )

    encoded_session_token = jwt.encode(
        {
            "exp": datetime.utcnow() + timedelta(days=7),
            "session_id": new_session.session_id,
            "token": new_authorized_user.internal_token
        },
        quadrant_config.Security.cookie_secret.value,
        algorithm="HS256"
    )
    token_type = "Bot" if new_authorized_user.user.is_bot else "Bearer"
    session_token = f"{token_type} {encoded_session_token}"

    # TODO: decide if it should be secure cookie or not
    response.set_cookie(
        key="session_token", value=session_token,
        secure=True, max_age=int(timedelta(days=7).total_seconds())
    )
