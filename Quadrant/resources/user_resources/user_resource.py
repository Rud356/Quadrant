from uuid import UUID

from fastapi import status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import NoResultFound

from Quadrant.middlewares.custom_objects import RequestWithAuthorizedUser
from Quadrant.models.users_package import User
from Quadrant.resources.utils import require_authorization
from Quadrant.schemas import HTTPError, user_schemas
from .router import router


@router.get(
    "/api/v1/users/me",
    description="Gives information about authorized user",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    }
)
@require_authorization
async def get_user_info_about_authorized(request: RequestWithAuthorizedUser):
    return request.authorized_user.user.as_dict()


@router.get(
    "/api/v1/users/{user_id}",
    description="Gives information about user",
    responses={
        200: {"model": user_schemas.UserSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPError},
        status.HTTP_404_NOT_FOUND: {"model": HTTPError}
    }
)
@require_authorization
async def get_user_info_about(user_id: UUID, request: RequestWithAuthorizedUser):
    try:
        user = await User.get_user(user_id, session=request.sql_session)

    except NoResultFound:
        return ORJSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"reason": "NOT_FOUND", "message": "User with given id not found"}
        )

    return user.as_dict()

