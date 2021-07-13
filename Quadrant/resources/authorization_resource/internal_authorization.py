from fastapi import HTTPException, Request, Response, status
from sqlalchemy.exc import NoResultFound

from Quadrant.models.users_package import UserInternalAuthorization
from Quadrant.resources.utils import prepare_users_client_authorization
from Quadrant.schemas import http_error_example, user_schemas
from .router import router


@router.post(
    "/api/v1/authorization/internal",
    description="Authorizes internally created user",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_400_BAD_REQUEST: {
            "model": http_error_example(
                "ALREADY_AUTHORIZED", "You are already authorized"
            )
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": http_error_example(
                "INVALID_CREDENTIALS", "You provided invalid login or password"
            )
        }
    },
    tags=["Authorization and registration"]
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
    await prepare_users_client_authorization(authorized_user, sql_session, request, response)

    return user_data
