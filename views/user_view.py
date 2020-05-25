import asyncio
from asyncio import sleep

from bson import ObjectId
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, field

from utils import exclude_keys

from models import Status
from models import Message
from models import UserModel
from models import MetaEndpoint, TextEndpoint

#TODO: add auto cleaner of inactive users
connected_users = {}


@dataclass
class User(UserModel):
    connected: list = field(default_factory=list)
    message_queue: list = field(default_factory=list)
    connections_to_clear: list = field(default_factory=list)

    def logout(self):
        self.connected.clear()
        self.message_queue.clear()
        connected_users.pop(self._id)

    async def friend_code_request(self, code: str):
        user_id = await self._friend_code_owner(code)

        return await self.send_friend_request(user_id)

    async def get_friends(self):
        friend_users = []
        offline_friends = set()

        for friend_id in self.friends:
            friend_view: User = connected_users.get(friend_id)

            if friend_view:
                friend_users.append(friend_view)

            else:
                offline_friends.add(friend_id)

        batched_friends = await super().get_friends(offline_friends)

        return friend_users + batched_friends

    async def batch_get_blocked(self):
        blocked_users = []
        offline_blocked = set()

        for blocked_id in self.blocked:
            blocked_view: User = connected_users.get(blocked_id)

            if blocked_view:
                blocked_users.append(blocked_view.public_dict)

            else:
                offline_blocked.add(blocked_id)

        batched_blocked = await super().get_blocked(offline_blocked)

        return blocked_users + batched_blocked

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

        connected_users.pop(self._id)

    @classmethod
    async def authorize(cls, login='', password='', token=''):
        user: UserModel = await super().authorize(login, password, token)

        view_user = cls(**user.__dict__)

        if view_user._id in connected_users:
            connected = connected_users[view_user._id]

            for k in connected.__dict__:
                if k in {'connected', 'message_queue', 'connections_to_clear'}:
                    continue

                connected.__dict__[k] = view_user.__dict__[k]

        else:
            connected_users[user._id] = view_user

        return view_user

    @classmethod
    async def from_id(cls, user_id: ObjectId):
        user = connected_users.get(user_id) or await super().from_id(user_id)

        user_view = cls(**user.__dict__)

        return user_view
