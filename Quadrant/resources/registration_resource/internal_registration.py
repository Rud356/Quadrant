from fastapi import HTTPException, Request, Response, status

from Quadrant.config import quadrant_config
from Quadrant.models.users_package import UserInternalAuthorization
from Quadrant.resources.utils import prepare_users_client_authorization
from Quadrant.schemas import http_error_example, user_schemas
from sqlalchemy.exc import IntegrityError
from .router import router


@router.post(
    "/api/v1/registration/internal",
    description="Authorizes internally created user",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "ALREADY_AUTHORIZED", "You are authorized"
            )
        },
        status.HTTP_403_FORBIDDEN: {
            "model": http_error_example(
                "REGISTRATION_DISABLED", "Registration was disabled"
            )
        },
        status.HTTP_409_CONFLICT: {
            "model": http_error_example(
                "LOGIN_ALREADY_IN_USE", "This login is already registered"
            )
        }
    },
    tags=["Authorization and registration"]
)
async def internal_registration(
    request: Request,
    response: Response,
    authorization_request: user_schemas.UserRegistration
):
    # TODO: add way to disable registration
    if quadrant_config.disable_registration.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "REGISTRATION_DISABLED",
                "message": "Registration was disabled"
            }
        )

    if "authorized_user" in request.scope:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "reason": "ALREADY_AUTHORIZED",
                "message": "You are authorized"
            }
        )

    user_schemas.UserRegistration.validate(authorization_request)

    sql_session = request.scope["sql_session"]
    try:
        new_authorized_user = await UserInternalAuthorization.register_user_internally(
            authorization_request.username, authorization_request.login,
            authorization_request.password, session=sql_session
        )

    except IntegrityError:
        raise HTTPException(409, {
            "reason": "LOGIN_ALREADY_IN_USE",
            "message": "This login is already registered"
        })

    await prepare_users_client_authorization(new_authorized_user, sql_session, request, response)
    return new_authorized_user.user.as_dict()
