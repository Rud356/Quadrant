from typing import Any

from sqlalchemy import exc
from tornado.log import app_log
from tornado.web import authenticated, Finish

from Quadrant.models import users_package
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class InternalAuthorizationHandler(QuadrantAPIHandler):
    """
    API endpoint that handles users internal authorization
    """

    session: Any

    async def post(self):
        """
        Handles user authorization
        ---
        description: Authorizes user in Quadrant with login and password
        security: []
        consumes:
          - multipart/form-data
        parameters:
        - in: formData
          name: login
          type: string
          required: true
          description: Users account login.
        - in: formData
          name: password
          type: string
          required: true
          description: Users account password.
        responses:
            200:
                description: Authorization succeed
                content:
                    application/json:
                        schema: UserLoginResponseSchema
                headers:
                    Set-Cookie:
                        schema:
                             - cookieAuth
                             - sessionID
            401:
                description: User did provided invalid authorization information
                content:
                    application/json:
                        schema: JsonHTTPError
            400:
                description: User didn't provided authorization information
                content:
                    application/json:
                        schema: JsonHTTPError
            404:
                description: User with this login doesn't exists
                content:
                    application/json:
                        schema: JsonHTTPError
        """
        # TODO: add TOPT later
        login = self.get_body_argument("login", default=None)
        password = self.get_body_argument("password", default=None)

        if login is None or password is None:
            app_log.debug(f"User did not provided login or password from IP {self.request.remote_ip}")
            raise JsonHTTPError(
                status_code=400,
                reason="No login or password was provided"
            )

        try:
            authorized_user = await users_package.UserInternalAuthorization.authorize(
                login, password, session=self.session
            )

        except ValueError:
            # TODO: add to user request limiter
            app_log.warn(f"User failed logging in from IP {self.request.remote_ip}")
            raise JsonHTTPError(
                status_code=401,
                log_message=f"User tried to log in with invalid password from IP {self.request.remote_ip}",
            )

        except exc.NoResultFound:
            app_log.debug(f"User with login {login} doesn't exists")
            raise JsonHTTPError(
                status_code=404,
                reason="User with this login doesn't exists"
            )

        user_data = authorized_user.user.as_dict()
        new_session = await users_package.UserSession.new_session(
            authorized_user.user, self.request.remote_ip, session=self.session
        )
        self.write(
            JsonWrapper.dumps(
                {"authorized": True, "user_data": user_data, "current_session_id": new_session.session_id}
            )
        )
        token_type = "Bot" if authorized_user.user.is_bot else "Bearer"
        token = f"{token_type} {authorized_user.internal_token}"
        self.set_secure_cookie("token", token, expires_days=2)
        self.set_secure_cookie("session_id", new_session.session_id, expires_days=2)
        raise Finish()

    # TODO: move method to sessions management
    @authenticated
    async def delete(self):
        """
        Terminates current users session
        ---
        security:
        requestBody:
            required: false
        responses:
            200:
                description: Authorization succeed
                content:
                    application/json:
                        schema: UserLoginResponseSchema
        """
        await self.user_session.terminate_session(session=self.session)
        self.clear_cookie("token")
        self.clear_cookie("session_id")
        self.write(JsonWrapper.dumps(
            {"success": True, "message": "You've been successfully logged off"}
        ))
        raise Finish()
