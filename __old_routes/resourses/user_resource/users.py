from uuid import UUID

from tornado.web import Finish
from sqlalchemy import exc

from Quadrant.models import users_package
from __old_routes.resourses.quadrant_api_handler import QuadrantAPIHandler
from __old_routes.resourses.utils import JsonHTTPError, JsonWrapper
from __old_routes.resourses.middlewares import rest_authenticated


class UserResourceHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self, user_id: str):
        """
        Represents users profile
        ---
        description: Displays information about existing not banned user.
        security:
            - sessionID
              cookieAuth

        parameters:
        - in: path
            name: user_id
            type: string
            format: uuid
            required: true

        responses:
            200:
                description: Found existing (and not banned) user and giving his details.
                content:
                    application/json:
                        schema: UserSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
            404:
                description: User not found or was banned.
                application/json:
                    schema: APIErrorSchema
        """
        try:
            user_id: UUID = UUID(user_id)
            user = await users_package.User.get_user(user_id, session=self.session)

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(404, reason="User with provided id not found")

        self.write(JsonWrapper.dumps(user.as_dict()))
        raise Finish()

    # TODO: add ability to ban some user by admins
    # TODO: add ability to delete account
