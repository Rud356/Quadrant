from app import client

from .enums import ChannelType
from .invite import Invite
from .message import Message

from bson import ObjectId
from typing import List, Dict, overload, final
from datetime import datetime
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorCollection

db: AsyncIOMotorCollection = client.endpoints


async def check_valid_user(user_id: ObjectId):
    users_db = client.chat_users
    user = await users_db.count_documents({'_id': user_id})
    return bool(user)


@dataclass
class TextEndpoint:
    _id: ObjectId
    _type: int
    members: List[ObjectId]
    last_message: ObjectId
    created_at: datetime

    @classmethod
    async def create_endpoint(cls, **kwargs): ...

    async def create_invite(
        self, requester: ObjectId,
        users_limit: int = -1,
        expires_at: datetime = datetime(2100, 12, 31)
        ):
        if requester not in self.members:
            raise self.exc.NotGroupMember("User isn't a part of group")

        return await Invite.create_invite(
            self._id, requester, users_limit,
            expires_at
        )


    async def send_message(self, author: ObjectId, content: str, files: List[str]):
        if author not in self.members:
            raise self.exc.NotGroupMember("User isn't a part of group")

        new_message = await Message.send_message(
            author, self._id, content, files
        )

        return new_message

    async def delete_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember("User trying to edit message in invalid group")

        return await Message.delete_message(requester, message_id)

    async def force_delete(self, requester: ObjectId, message_id: ObjectId):
        raise self.exc.EndpointException("Not realisated")

    async def edit_message(self, requester: ObjectId, message_id: ObjectId, content: str):
        if requester not in self.members:
            raise self.exc.NotGroupMember("User trying to edit message in invalid group")

        return await Message.edit_message(requester, message_id, content)

    async def pin_message(self, requester: ObjectId, message_id: ObjectId, pin: bool = True):
        if requester not in self.members:
            raise self.exc.NotGroupMember("User trying to edit message in invalid group")

        return await Message.set_message_pin(requester, message_id, pin)

    class exc:
        class EndpointException(Exception): ...
        class NotGroupMember(EndpointException): ...
        class UnsupprotedMethod(EndpointException): ...
        class NoPermissionForAction(EndpointException): ...

@final
@dataclass
class DMchannel(TextEndpoint):
    @overload
    async def create_invite(self, *args, **kwargs):
        raise self.exc.UnsupprotedMethod("Can't create invite to dm")

    @overload
    @classmethod
    async def create_endpoint(cls, user_init: ObjectId, user_accept: ObjectId):
        if not (
            await check_valid_user(user_accept) and
            await check_valid_user(user_init)
            ):
            raise ValueError("One of two users is invalid")

        new_dm = {
            "_type": ChannelType.dm,
            "members": [user_init, user_accept],
            "created_at": datetime.utcnow(),
            "last_message": None
        }
        id = await db.insert_one(new_dm).inserted_id

        return cls(_id = id, **new_dm)
