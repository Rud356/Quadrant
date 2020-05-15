from typing import List, Dict
from bson import ObjectId
from datetime import datetime
from dataclasses import dataclass, field

from models import User as UserModel
from models import Message
from models import MetaEndpoint, DMchannel, TextEndpoint

from .status_enum import Status

users_connected_ids = {}


@dataclass
class UserView(UserModel):
    # TODO: maybe add saving of users states
    status: int = Status.online
    connected: list = []

    async def set_status(self, status: int):
        if status not in list(Status):
            raise ValueError("Wrong status")

        self.status = status

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
        users_connected_ids[user._id] = view_user

    @classmethod
    async def from_id(cls, user_id: ObjectId):
        user = users_connected_ids.get(user_id) or await super().from_id(user_id)

        user_view = cls(**user.__dict__)

        return user_view

    def make_connection(self, ws):
        # this function puts new websocket in list
        self.connected.append(ws)

    def make_disconnect(self, ws):
        # this function deletes disconnected websockets
        self.connected.remove(ws)

    async def broadcast_message(self, message):
        # TODO: write sending to all connected websockets
        ...

    def logout(self):
        # TODO: close all websockets
        users_connected_ids.pop(self._id)

    def public_dict(self):
        return {
            '_id': self._id,
            "status": self.status,
            "text_status": self.text_status,
            "bot": self.bot,
            "nick": self.nick,
            "created_at": self.created_at,
        }
