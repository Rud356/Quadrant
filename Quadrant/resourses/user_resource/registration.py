from marshmallow import ValidationError
from tornado.escape import squeeze, xhtml_escape
from tornado.web import Finish

from Quadrant.models import users_package
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper
from .schemas import UserRegistrationSchema


class InternalRegistrationHandler(QuadrantAPIHandler):
    async def post(self):
        if self.get_current_user():
            raise JsonHTTPError(status_code=400, reason="User is authorized")

        registration_data = {
            "username": xhtml_escape(squeeze(self.get_body_argument("username", default=None))),
            "login": self.get_body_argument("login", default=None),
            "password": self.get_body_argument("password", default=None)
        }
        try:
            UserRegistrationSchema.validate(registration_data)

        except ValidationError as err:
            raise JsonHTTPError(status_code=400, reason=err.messages)

        await users_package.UserInternalAuthorization.register_user_internally(
            **registration_data, session=self.session
        )

        self.write(JsonWrapper.dumps({"success": True}))
        raise Finish()
