from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Request, Response, status
from sqlalchemy.exc import NoResultFound

from Quadrant.config import quadrant_config
from Quadrant.models.users_package import UserInternalAuthorization, UserSession
from Quadrant.schemas import HTTPError, user_schemas
from .router import router


@router.post(
    "/api/v1/authorization/internal",
    description="Authorizes internally created user",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPError},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError}
    },
    tags=["Authorization"]
)
async def internal_authorization(
    request: Request,
    response: Response,
    authorization_request: user_schemas.UserAuthorization
):
    # TODO: work with security here
    sql_session = request.scope["sql_session"]

    if "authorized_user" in request.scope:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"reason": "ALREADY_AUTHORIZED", "message": "You are already authorized"}
        )

    try:
        authorized_user = await UserInternalAuthorization.authorize(
            authorization_request.login, authorization_request.password, session=sql_session
        )

    except (ValueError, NoResultFound):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"reason": "INVALID_CREDENTIALS", "message": "You provided invalid login or password"}
        )

    user_data = authorized_user.user.as_dict()
    new_session = await UserSession.new_session(
        authorized_user.user, request.client.host, session=sql_session
    )

    encoded_session_token = jwt.encode(
        {
            "exp": datetime.utcnow() + timedelta(days=7),
            "session_id": new_session.session_id,
            "token": authorized_user.internal_token
        },
        quadrant_config.Security.cookie_secret.value,
        algorithm="HS256"
    )
    token_type = "Bot" if authorized_user.user.is_bot else "Bearer"
    session_token = f"{token_type} {encoded_session_token}"

    # TODO: decide if it should be secure cookie or not
    response.set_cookie(
        key="session_token", value=session_token,
        secure=True, max_age=int(timedelta(days=7).total_seconds())
    )

    return user_data
