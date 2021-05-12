from uuid import UUID

from tornado.web import authenticated

from Quadrant.models import users_package
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class RelationsCheckHandler(QuadrantAPIHandler):
    @authenticated
    async def get(self, with_user_id):
        try:
            with_user_id: UUID = UUID(with_user_id)

        except ValueError:
            raise JsonHTTPError(status_code=404, reason="Invalid user id")

        relation = await users_package.UsersRelations.get_exact_relationship_status(
            self.user.id, with_user_id, session=self.session
        )

        self.write(
            JsonWrapper.dumps({"with_user_id": with_user_id, "status": relation})
        )
