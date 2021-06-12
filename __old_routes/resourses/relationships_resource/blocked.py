from uuid import UUID

from sqlalchemy import exc

from Quadrant.models import users_package
from __old_routes.resourses.middlewares import rest_authenticated
from __old_routes.resourses.quadrant_api_handler import QuadrantAPIHandler
from __old_routes.resourses.utils import JsonHTTPError, JsonWrapper


class BlockedRelationsHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def post(self, blocking_user_id):
        try:
            user_id: UUID = UUID(blocking_user_id)
            blocking_user = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.block_user(self.user, blocking_user, session=self.session)

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.AlreadyBlockedException:
            raise JsonHTTPError(status_code=400, reason="You already blocked this user")

        # TODO: notify user about new friend request
        self.write(JsonWrapper.dumps({"blocked_id": blocking_user_id}))

    @rest_authenticated
    async def delete(self, blocked_user_id):
        try:
            user_id: UUID = UUID(blocked_user_id)
            blocking_user = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.unblock_user(self.user, blocking_user, session=self.session)

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.RelationshipsException:
            raise JsonHTTPError(status_code=400, reason="User isn't blocked")

        self.write(JsonWrapper.dumps({"unblocked_user_id": blocked_user_id}))


class BlockedRelationsPageHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        page = self.get_argument("page", default="0")
        try:
            page = int(page)
            relation_type = users_package.UsersRelationType.blocked
            relations_page = await users_package.UsersRelations.get_relationships_page(
                self.user, page, relation_type, session=self.session
            )

        except ValueError:
            raise JsonHTTPError(status_code=400, reason="Invalid page number")

        self.write(JsonWrapper.dumps(
            {
                "relation_status": relation_type,
                "users": [user.as_dict() for _, user in relations_page]
            }
        ))
