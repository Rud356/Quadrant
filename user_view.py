import asyncio
from asyncio import sleep
from dataclasses import dataclass, field
from time import time

from bson import ObjectId

from app import app, connected_users
from models.enums import UpdateType
from models.user_model import UserModel
from models.message_model import UpdateMessage

TTK = app.config["TTK"]
tokenized_connected_users = {}


@dataclass
class User(UserModel):
    connected: list = field(default_factory=list)
    message_queue: list = field(default_factory=list)
    kill_websockets: list = field(default_factory=list)
    last_used_api_timestamp: float = time()

    @classmethod
    async def authorize(cls, login='', password='', token=''):
        if token:
            user_view: User = tokenized_connected_users.get(token)

            if not user_view:
                user: UserModel = await super().authorize(
                    login, password, token
                )

                user_view = cls(**user.__dict__)
                user_view.start_alive_checker()
                connected_users[user_view._id] = user_view
                tokenized_connected_users[user_view.token] = user_view

        elif login and password:
            user: UserModel = await super().authorize(
                login, password, token
            )

            user_view = cls(**user.__dict__)

            if user_view._id not in connected_users:
                user_view.start_alive_checker()
                connected_users[user_view._id] = user_view
                tokenized_connected_users[user_view.token] = user_view

            else:
                user_view = connected_users.get(user_view._id)

        else:
            raise ValueError("Not enough auth info")

        user_view.last_used_api_timestamp = time()
        return user_view

    @classmethod
    async def from_id(cls, user_id: ObjectId):
        user = connected_users.get(user_id) or await super().from_id(user_id)

        user_view = cls(**user.__dict__)

        return user_view

    async def delete_user(self):
        tokenized_connected_users.pop(self.token)
        await super().delete_user()

    def logout(self):
        if connected_users.pop(self._id, False):
            self.connected.clear()
            self.message_queue.clear()

    def start_alive_checker(self):
        asyncio.ensure_future(self.check_user_alive())

    async def check_user_alive(self):
        ticks = 0

        while True:
            if len(self.connected):
                ticks = 0

            else:
                ticks += 1

            if ticks == TTK:
                break

            api_usage_gap = time() - self.last_used_api_timestamp
            if api_usage_gap > TTK * 60 and not len(self.connected):
                break

            await sleep(60)

        self.logout()

    async def friend_code_request(self, friend_code: str):
        user_id = await self._friend_code_owner(friend_code)
        await self.send_friend_request(user_id)

    async def add_message(self, message):
        if self.connected:
            self.message_queue.append(message)

    async def add_ws(self, ws):
        self.connected.append(ws)

        # The first connected websocket
        if len(self.connected) == 1:
            asyncio.ensure_future(self.run_websocket())

    async def run_websocket(self):
        while len(self.connected):

            await sleep(0.1)
            messages_queue_len = len(self.message_queue)

            for _ in range(messages_queue_len):
                message = self.message_queue.pop(0)

                for ws in self.connected:
                    ws.message_pool.append(message)

            for remove_index in self.kill_websockets:
                self.connected.pop(remove_index)

            self.kill_websockets.clear()

        self.logout()

    async def broadcast_to_friends(self, update_message):
        send_to_users = [self._id] + self.friends
        for friend_id in send_to_users:
            friend = connected_users.get(friend_id)

            # If user is offline
            if not friend:
                continue

            await friend.add_message(update_message)

    async def send_friend_request(self, to_user_id: ObjectId):
        await super().send_friend_request(to_user_id)
        self.pendings_outgoing.append(to_user_id)

        requested: User = connected_users.get(to_user_id)
        requested.pendings_incoming.append(self._id)

        friend_request = UpdateMessage(
            {
                "_id": self._id
            },
            UpdateType.new_friend_request
        )
        await requested.add_message(friend_request)

    async def response_friend_request(self, user_id: ObjectId, confirm=True):
        await super().response_friend_request(user_id, confirm)

        self.pendings_incoming.remove(user_id)

        responding_to_user: User = connected_users.get(user_id)

        if not responding_to_user:
            return

        responding_to_user.pendings_outgoing.remove(self._id)

        if confirm:
            responding_to_user.friends.append(self._id)
            self.friends.append(user_id)

            new_friend = UpdateMessage(
                {
                    "_id": self._id
                },
                UpdateType.new_friend
            )
            await responding_to_user.add_message(new_friend)

        else:
            rejected_friend_request = UpdateMessage(
                {
                    "_id": self._id
                },
                UpdateType.friend_request_rejected
            )
            await responding_to_user.add_message(rejected_friend_request)

    async def cancel_friend_request(self, user_id: ObjectId):
        await super().cancel_friend_request(user_id)
        self.pendings_outgoing.remove(user_id)

        canceled_to_user: User = connected_users.get(user_id)

        if canceled_to_user:
            canceled_to_user.pendings_incoming.remove(self._id)
            cancel_friend_request = UpdateMessage(
                {
                    "_id": self._id
                },
                UpdateType.friend_request_canceled
            )
            await canceled_to_user.add_message(cancel_friend_request)

    async def delete_friend(self, user_id: ObjectId):
        await super().delete_friend(user_id)
        self.friends.remove(user_id)

        deleted_friend: User = connected_users.get(user_id)

        if deleted_friend:
            deleted_friend.friends.remove(self._id)

            update_friend_removed = UpdateMessage(
                {
                    "_id": self._id
                },
                UpdateType.friend_deleted
            )
            await deleted_friend.add_message(update_friend_removed)

    async def block_user(self, blocking: ObjectId):
        await super().block_user(blocking)

        self.blocked.append(blocking)
        blocked_user: User = connected_users.get(blocking)

        if not blocked_user:
            return

        if blocking in self.friends:
            self.friends.remove(blocking)
            blocked_user.friends.remove(self._id)

        elif blocking in self.pendings_incoming:
            self.pendings_incoming.remove(blocking)
            blocked_user.pendings_outgoing.remove(self._id)

        elif blocking in self.pendings_outgoing:
            self.pendings_outgoing.remove(blocking)
            blocked_user.pendings_incoming.remove(self._id)

        got_blocked_by = UpdateMessage(
            {
                "_id": self._id
            },
            UpdateType.got_blocked
        )
        await blocked_user.add_message(got_blocked_by)

    async def unblock_user(self, unblocking: ObjectId):
        await super().unblock_user(unblocking)
        self.blocked.remove(unblocking)

    # Pagination methods
    async def paged_incoming_requests(self, page: int = 0):
        cursor = self.aggregation_paged_incoming_requests(page)
        users = []

        async for user in cursor:
            cached: User = connected_users.get(user['_id'])

            if cached:
                users.append(cached.public_dict)

            else:
                users.append(user)

        return users

    async def paged_outgoing_requests(self, page: int = 0):
        cursor = self.aggregation_paged_outgoing_requests(page)
        users = []

        async for user in cursor:
            cached: User = connected_users.get(user['_id'])

            if cached:
                users.append(cached.public_dict)

            else:
                users.append(user)

        return users

    async def paged_friends(self, page: int = 0):
        cursor = self.aggregation_paged_friends(page)
        users = []

        async for user in cursor:
            cached: User = connected_users.get(user['_id'])

            if cached:
                users.append(cached.public_dict)

            else:
                users.append(user)

        return users

    async def paged_blocked(self, page: int = 0):
        cursor = self.aggregation_paged_blocked(page)
        users = []

        async for user in cursor:
            cached: User = connected_users.get(user['_id'])

            if cached:
                users.append(cached.public_dict)

            else:
                users.append(user)

        return users
