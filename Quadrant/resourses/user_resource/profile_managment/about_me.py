from tornado.web import Finish

from Quadrant.resourses.middlewares import rest_authenticated
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonWrapper


class AboutMeHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        """
        Represents users profile
        ---
        description: Displays information about existing not banned user.
        security:
            - sessionID
              cookieAuth

        responses:
            200:
                description: Found existing (and not banned) user and giving his details.
                content:
                    application/json:
                        schema: UserPrivateSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
            404:
                description: User not found or was banned.
                application/json:
                    schema: APIErrorSchema
        """
        user = self.user
        self.write(JsonWrapper.dumps(user.as_dict(public_view=False)))
        raise Finish()

    @rest_authenticated
    async def delete(self):
        # TODO: add method to delete user
        pass
