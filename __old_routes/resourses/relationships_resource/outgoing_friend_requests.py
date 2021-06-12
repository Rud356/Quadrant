from uuid import UUID

from sqlalchemy import exc

from Quadrant.models import users_package
from __old_routes.resourses.middlewares import rest_authenticated
from __old_routes.resourses.quadrant_api_handler import QuadrantAPIHandler
from __old_routes.resourses.utils import JsonHTTPError, JsonWrapper


class OutgoingFriendRequestHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def post(self, request_to_id):
        if self.user.is_bot:
            raise JsonHTTPError(status_code=400, reason="Bot users can not send friend requests")

        try:
            user_id: UUID = UUID(request_to_id)
            request_to = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.send_friend_request(self.user, request_to, session=self.session)

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.RelationshipsException:
            raise JsonHTTPError(status_code=400, reason="You and this user already have relations")

        except users_package.User.exc.UserIsBot:
            raise JsonHTTPError(status_code=400, reason="Bots can not receive friend requests")

        # TODO: notify user about new friend request
        self.write(JsonWrapper.dumps({"sent_friend_request_to": request_to_id}))

    @rest_authenticated
    async def delete(self, request_to_id):
        try:
            user_id: UUID = UUID(request_to_id)
            request_to = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.cancel_friend_request(self.user, request_to, session=self.session)

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.RelationshipsException:
            raise JsonHTTPError(status_code=400, reason="You did not sent friend request to this user")

        # TODO: notify user about new friend request
        self.write(JsonWrapper.dumps({"cancelled_friend_request_to": request_to_id}))


class OutgoingFriendsRequestsPageHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        page = self.get_argument("page", default="0")
        try:
            page = int(page)
            relation_type = users_package.UsersRelationType.friend_request_sender
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
