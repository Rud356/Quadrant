from typing import Optional

from Quadrant.middlewares import custom_objects
from Quadrant.models.users_package import User, UserInternalAuthorization, UserSession


class RequestWithAuthorizedUser(custom_objects.RequestWithSession):
    db_user: Optional[User]
    authorized_user: Optional[UserInternalAuthorization]
    user_session: Optional[UserSession]
