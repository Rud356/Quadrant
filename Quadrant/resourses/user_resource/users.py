from uuid import UUID

from tornado.web import Finish
from sqlalchemy import exc

from Quadrant.models import users_package
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper
from Quadrant.resourses.middlewares import rest_authenticated


class UserResourceHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self, user_id: str):
        try:
            user_id: UUID = UUID(user_id)
            user = await users_package.User.get_user(user_id, session=self.session)

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(404, reason=f"User with provided id not found")

        self.write(JsonWrapper.dumps(user.as_dict()))
        raise Finish()

    # TODO: add ability to ban some user by admins
