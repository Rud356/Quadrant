from uuid import UUID

from sqlalchemy import exc

from Quadrant.models import users_package
from Quadrant.resourses.middlewares import rest_authenticated
from Quadrant.resourses.quadrant_api_handler import QuadrantAPIHandler
from Quadrant.resourses.utils import JsonHTTPError, JsonWrapper


class IncomingFriendRequestHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def post(self, request_sender_id):
        if self.user.is_bot:
            raise JsonHTTPError(status_code=400, reason="Bot users can not have friend requests")

        try:
            user_id: UUID = UUID(request_sender_id)
            from_user = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.respond_on_friend_request(
                from_user, self.user, accept_request=True, session=self.session
            )

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.RelationshipsException:
            raise JsonHTTPError(status_code=400, reason="You and this user already have relations")

        # TODO: notify user about new friend request
        self.write(JsonWrapper.dumps({"accepted_friend_request_from": request_sender_id}))

    @rest_authenticated
    async def delete(self, request_sender_id):
        try:
            user_id: UUID = UUID(request_sender_id)
            from_user = await users_package.User.get_user(user_id, session=self.session)
            await users_package.UsersRelations.respond_on_friend_request(
                from_user, self.user, accept_request=False, session=self.session
            )

        except (exc.NoResultFound, ValueError):
            raise JsonHTTPError(status_code=404, reason=f"User with provided id not found")

        except users_package.UsersRelations.exc.RelationshipsException:
            raise JsonHTTPError(status_code=400, reason="You did not received friend request to this user")

        # TODO: notify user about new friend request
        self.write(JsonWrapper.dumps({"refused_friend_request_from": request_sender_id}))


class IncomingFriendsRequestsPageHandler(QuadrantAPIHandler):
    @rest_authenticated
    async def get(self):
        page = self.get_argument("page", default="0")
        try:
            page = int(page)
            relation_type = users_package.UsersRelationType.friend_request_receiver
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
