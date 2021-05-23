from sqlalchemy.exc import NoResultFound
from tornado.web import Finish

from Quadrant.models.users_package import UserSession
from Quadrant.resourses.middlewares import rest_authenticated
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class UsersCurrentSessionHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        if self.user.is_bot:
            raise JsonHTTPError(403, reason="Bots don't have sessions")

        self.write(
            JsonWrapper.dumps(self.user_session.as_dict())
        )
        raise Finish()

    @rest_authenticated
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
        if self.user.is_bot:
            raise JsonHTTPError(403, reason="Bots don't have sessions")

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


class UsersAliveSessionHandler(QuadrantAPIHandler):
    async def fetch_session(self, session_id: str) -> UserSession:
        try:
            session_id = int(session_id)

        except ValueError:
            raise JsonHTTPError(400, reason="Invalid session_id")

        if self.user.is_bot:
            raise JsonHTTPError(403, reason="Bots don't have sessions")

        try:
            fetched_session = await UserSession.get_user_session(
                self.auth_user.user_id, session_id, session=self.session
            )

        except NoResultFound:
            raise JsonHTTPError(404, reason="No session with requested id found.")

        return fetched_session

    @rest_authenticated
    async def get(self, session_id):
        if self.user.is_bot:
            raise JsonHTTPError(403, reason="Bots don't have sessions")

        fetched_session = await self.fetch_session(session_id)

        self.write(
            JsonWrapper.dumps(fetched_session.as_dict())
        )
        raise Finish()

    @rest_authenticated
    async def delete(self, session_id):
        """
        Terminates one exact users session
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


class UsersSessionsHistoryHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self, page):
        if self.user.is_bot:
            raise JsonHTTPError(403, reason="Bots don't have sessions")

        try:
            page = int(page)
            sessions = await UserSession.get_user_sessions_page(self.user.id, page, session=self.session)

        except ValueError:
            raise JsonHTTPError(400, reason="Invalid sessions page")

        self.write(
            JsonWrapper.dumps({
                "sessions": [session.as_dict() for session in sessions]
            })
        )


class UsersAllSessionsTerminationHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def delete(self):
        if self.user.is_bot:
            raise JsonHTTPError(403, reason="Bots don't have sessions")

        await UserSession.terminate_all_sessions(self.user.id, session=self.session)
        self.write(
            JsonWrapper.dumps({
                "success": True
            })
        )
