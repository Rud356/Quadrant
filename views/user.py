import asyncio
from typing import List, Dict
from bson import ObjectId
from datetime import datetime
from dataclasses import dataclass, field

from models import User as UserModel
from models import Message
from models.status_enum import Status
from models import MetaEndpoint, DMchannel, TextEndpoint



users_connected_ids = {}


@dataclass
class UserView(UserModel):
    connected: list = field(default_factory=list)
    message_queue: list = field(default_factory=list)
    to_clear_connections: list = field(default_factory=list)

    async def frined_code_request(self, code: str):
        user_id = await self.friendcodes_owner(code)
        if user_id is not None:
            raise ValueError("No such friend code")

        return await self.send_friend_request(user_id)

    @classmethod
    async def authorize(cls, login='', password='', token=''):
        if login and password:
            user: UserModel = await super().authorize(login, password)

        elif token:
            user = await super().authorize(token=token)

        view_user = cls(**user.__dict__)

        if view_user._id in users_connected_ids:
            view_user.status = users_connected_ids[view_user._id].status

        users_connected_ids[user._id] = view_user
        return view_user

    @classmethod
    async def from_id(cls, user_id: ObjectId):
        user = users_connected_ids.get(user_id) or await super().from_id(user_id)

        user_view = cls(**user.__dict__)

        return user_view

    async def batch_get_friends(self):
        friends_representations = []
        applied_ids = set()

        for friend in self.friends:
            view_friend: UserView = users_connected_ids.get(friend)

            if view_friend:
                friends_representations.append(view_friend.public_dict)
                applied_ids.add(view_friend._id)

        friends_set = set(self.friends)
        friends_unapplied = list(friends_set.difference(applied_ids))
        friends_to_apply = super().batch_get_friends(friends_unapplied)

        async for friend in friends_to_apply:
            friend_object = UserView(**friend)
            friends_representations.append(friend_object.public_dict)

        return friends_representations

    async def batch_get_blocked(self):
        blocked_repr = []
        async for blocked_user in super().batch_get_blocked():
            blocked_user_repr = UserView(**blocked_user).public_dict
            blocked_repr.append(blocked_user_repr)

        return blocked_repr

    async def add_ws(self, ws):
        ws.index = len(self.connected)
        self.connected.append(ws)

        if not len(self.connected):
            asyncio.ensure_future(self.run_websockets())

    async def run_websockets(self):
        while len(self.connected):
            await asyncio.sleep(0.1)
            messages_queue_len = len(self.message_queue)
            # this is made to have some small number of messages
            # so we cleaning up queue and also work on everything
            for _ in range(messages_queue_len):
                message = self.message_queue.pop(0)
                for ws in self.connected:
                    asyncio.ensure_future(ws(message))

            for clearing_index in self.to_clear_connections:
                self.connected.pop(clearing_index)

        users_connected_ids.pop(self._id)

    def logout(self):
        self.connected.clear()
        self.message_queue.clear()
        users_connected_ids.pop(self._id)

    @property
    def public_dict(self):
        return {
            '_id': self._id,
            "status": self.status,
            "text_status": self.text_status,
            "bot": self.bot,
            "nick": self.nick,
            "created_at": self.created_at,
        }

    @property
    def private_dict(self):
        # making sure that our object is new one
        output = dict(self.__dict__)
        output.pop('token', None)
        output.pop('connected', None)
        output.pop('message_queue', None)
        output.pop('to_clear_connections', None)
        return output
