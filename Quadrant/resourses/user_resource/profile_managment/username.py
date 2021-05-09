from tornado.escape import squeeze, xhtml_escape
from tornado.web import Finish, authenticated

from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class UsernameHandler(QuadrantAPIHandler):
    @authenticated
    async def post(self):
        try:
            username = xhtml_escape(squeeze(self.json_data["text_status"]))
            if len(username) == 0:
                raise JsonHTTPError(status_code=400, reason="Empty username field")
            await self.user.set_username(username, session=self.session)

        except KeyError:
            raise JsonHTTPError(status_code=400, reason="No username provided")

        self.write(JsonWrapper.dumps({"new_username": username}))
        # TODO: send notification about update
        raise Finish()
