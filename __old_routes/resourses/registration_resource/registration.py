from marshmallow import ValidationError
from tornado.escape import squeeze, xhtml_escape
from tornado.web import Finish

from Quadrant.models import users_package
from __old_routes.resourses.quadrant_api_handler import QuadrantAPIHandler
from __old_routes.resourses.utils import JsonHTTPError, JsonWrapper
from __old_routes.resourses.registration_resource.schemas import UserRegistrationSchema


class InternalRegistrationHandler(QuadrantAPIHandler):
    async def post(self):
        """
        Handles user registration inside of Quadrant only
        ---
        description: Handles user registration inside of Quadrant
        security: []

        consumes:
          - multipart/form-data

        parameters:
        - in: formData
            name: login
            type: string
            required: true
            description: Users account login.
            pattern: ^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$
            minLength: 8
            maxLength: 128


        - in: formData
            name: password
            type: string
            required: true
            description: Users account password.
            pattern: ^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$"
            minLength: 8
            maxLength: 128

        - in: formData
            name: username
            type: string
            required: true
            description: Users name that will be visible for everyone.
            minLength: 1
            maxLength: 50

        responses:
            200:
                description: represents that registration went ok.
                application/json:
                    schema: SuccessResponseSchema
            400:
                description: |
                    Represents that some fields are invalid and in response explains what fields were invalid.
                    In reason field you will have field name and explanation of what's wrong with it.

                application/json:
                    schema: APIErrorWithNestedDataSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
        """
        if self.get_current_user():
            raise JsonHTTPError(status_code=403, reason="User is authorized")

        registration_data = {
            "username": xhtml_escape(squeeze(self.get_body_argument("username", default=None))),
            "login": self.get_body_argument("login", default=None),
            "password": self.get_body_argument("password", default=None)
        }
        try:
            registration_data_validator = UserRegistrationSchema()
            registration_data_validator.validate(registration_data)

        except ValidationError as err:
            raise JsonHTTPError(status_code=400, reason=err.messages)

        await users_package.UserInternalAuthorization.register_user_internally(
            **registration_data, session=self.session
        )

        self.write(JsonWrapper.dumps({"success": True}))
        raise Finish()
