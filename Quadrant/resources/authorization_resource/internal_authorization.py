import jwt
from datetime import datetime, timedelta
from fastapi import status, Form, Response
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import NoResultFound

from Quadrant.config import quadrant_config
from Quadrant.middlewares.custom_objects import RequestWithAuthorizedUser
from Quadrant.models.users_package import UserInternalAuthorization, UserSession
from Quadrant.schemas import HTTPError, user_schemas
from .router import router


@router.post(
    "/api/v1/authorization/internal",
    description="Authorizes user, registered through Quadrant",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError},
    }
)
async def internal_authorization(
    request: RequestWithAuthorizedUser,
    response: Response,
    login: str = Form(...),
    password: str = Form(...)
):
    # TODO: work with csrf form protection?
    if request.user is not None:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"reason": "ALREADY_AUTHORIZED", "message": "You are already authorized"}
        )

    try:
        authorized_user = await UserInternalAuthorization.authorize(
            login, password, session=request.sql_session
        )

    except (ValueError, NoResultFound):
        return ORJSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"reason": "INVALID_CREDENTIALS", "message": "You provided invalid login or password"}
        )

    user_data = authorized_user.user.as_dict()
    new_session = await UserSession.new_session(
        authorized_user.user, request.client.host, session=request.sql_session
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
