from uuid import UUID

from sqlalchemy import exc

from Quadrant.models import users_package
from Quadrant.resourses.middlewares import rest_authenticated
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class FriendsRelationsHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def delete(self, friend_user_id):
        try:
            user_id: UUID = UUID(friend_user_id)
            friend = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.remove_user_from_friends(
                self.user, friend, session=self.session
            )

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.RelationshipsException:
            raise JsonHTTPError(status_code=400, reason="User isn't your friend")

        self.write(JsonWrapper.dumps({"unfriended_user_id": friend_user_id}))


class FriendsRelationsPageHandler(QuadrantAPIHandler):
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
