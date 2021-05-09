from tornado.web import Finish, authenticated

from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class UserStatusHandler(QuadrantAPIHandler):
    @authenticated
    async def post(self):
        try:
            status = self.get_query_argument("status", default=None)
            await self.user.set_status(status, session=self.session)

        except KeyError:
            raise JsonHTTPError(status_code=400, reason="Invalid status name for user")

        self.write(JsonWrapper.dumps({"new_status": status}))
        # TODO: send notification about update
        raise Finish()
