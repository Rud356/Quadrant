from sqlalchemy.exc import NoResultFound
from tornado.web import Finish

from Quadrant.models.users_package import UserSession
from __old_routes.resourses.middlewares import rest_authenticated
from __old_routes.resourses.quadrant_api_handler import QuadrantAPIHandler
from __old_routes.resourses.utils import JsonHTTPError, JsonWrapper


class UsersCurrentSessionHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        """
        Sends users current session representation
        ---
        description: Sends users current session representation.
        security:
            - sessionID
              cookieAuth

        requestBody:
            required: false

        responses:
            200:
                description: Shows details on current user session.
                content:
                    application/json:
                        schema: UserSessionSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
        """
        self.write(
            JsonWrapper.dumps(self.user_session.as_dict())
        )
        raise Finish()

    @rest_authenticated
    async def delete(self):
        """
        Terminates current users session.
        ---
        description: Terminates current users session.
        security:
            - sessionID
              cookieAuth

        requestBody:
            required: false

        responses:
            200:
                description: Session has been terminated.
                content:
                    application/json:
                        schema: SessionTerminationResponseSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
        """
        session_id = self.user_session.session_id

        await self.user_session.terminate_session(session=self.session)
        self.clear_cookie("token")
        self.clear_cookie("session_id")

        self.write(JsonWrapper.dumps(
            {
                "success": True,
                "message": "You've been successfully logged off",
                "terminated_session_id": session_id
            }
        ))
        raise Finish()


class UsersExactSessionHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self, session_id):
        """
        Sends users exact session representation
        ---
        description: Sends users exact session representation.
        security:
            - sessionID
              cookieAuth

        parameters:
        - in: path
            name: session_id
            type: integer

        requestBody:
            required: false

        responses:
            200:
                description: Shows details on current user session.
                content:
                    application/json:
                        schema: UserSessionSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
        """
        fetched_session = await self.fetch_session(session_id)

        self.write(
            JsonWrapper.dumps(fetched_session.as_dict())
        )
        raise Finish()

    @rest_authenticated
    async def delete(self, session_id):
        """
        Terminates users specific session.
        ---
        description: Terminates users specific session.
        security:
            - sessionID
              cookieAuth

        requestBody:
            required: false

        responses:
            200:
                description: Session has been terminated.
                content:
                    application/json:
                        schema: SessionTerminationResponseSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
            404:
                description: Session not found.
                application/json:
                    schema: APIErrorSchema
        """
        fetched_session = await self.fetch_session(session_id)
        await fetched_session.terminate_session(session=self.session)
        self.write(JsonWrapper.dumps(
            {
                "success": True,
                "message": "You've been successfully logged off on session specified session",
                "terminated_session_id": session_id
            }
        ))
        raise Finish()

    async def fetch_session(self, session_id: str) -> UserSession:
        try:
            session_id = int(session_id)

        except ValueError:
            raise JsonHTTPError(404, reason="Invalid session_id")

        try:
            fetched_session = await UserSession.get_user_session(
                self.auth_user.user_id, session_id, session=self.session
            )

        except NoResultFound:
            raise JsonHTTPError(404, reason="No session with requested id found.")

        return fetched_session


class UsersSessionsHistoryHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        """
        Sends user sessions page representation
        ---
        security:
            - sessionID
              cookieAuth

        requestBody:
            required: false

        responses:
            200:
                description: Shows details on current user session.
                content:
                    application/json:
                        schema: UserSessionsPageSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
            404:
                description: Invalid page number and so nothing found.
                application/json:
                    schema: APIErrorSchema
        """
        page = self.get_argument("page", default="0")
        try:
            page = int(page)
            sessions = await UserSession.get_user_sessions_page(self.user.id, page, session=self.session)

        except ValueError:
            raise JsonHTTPError(404, reason="Invalid sessions page")

        self.write(
            JsonWrapper.dumps({
                "sessions": [session.as_dict() for session in sessions]
            })
        )


class UsersAllSessionsTerminationHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def delete(self):
        """
        Terminates all users sessions.
        ---
        description: Terminates users specific session.
        security:
            - sessionID
              cookieAuth

        requestBody:
            required: false

        responses:
            200:
                description: Session has been terminated.
                content:
                    application/json:
                        schema: SuccessResponseSchema
            403:
                description: Unauthorized.
                application/json:
                    schema: APIErrorSchema
        """
        await UserSession.terminate_all_sessions(self.user.id, session=self.session)
        self.write(
            JsonWrapper.dumps({
                "success": True
            })
        )
