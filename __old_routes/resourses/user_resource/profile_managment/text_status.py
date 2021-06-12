from tornado.escape import squeeze, xhtml_escape
from tornado.web import Finish, authenticated

from __old_routes.resourses.quadrant_api_handler import QuadrantAPIHandler
from __old_routes.resourses.utils import JsonHTTPError, JsonWrapper


class UserTextStatusHandler(QuadrantAPIHandler):
    @authenticated
    async def post(self):
        try:
            text_status = xhtml_escape(squeeze(self.json_data["text_status"]))
            await self.user.set_text_status(text_status, session=self.session)

        except KeyError:
            raise JsonHTTPError(status_code=400, reason="No text status provided")

        self.write(JsonWrapper.dumps({"new_text_status": text_status}))
        # TODO: send notification about update
        raise Finish()
