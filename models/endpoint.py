from bson import ObjectId
from typing import List, Dict, overload
from datetime import datetime
from dataclasses import dataclass, field

# my module
from app import db
from .enums import ChannelType
from .invite import Invite
from .message import Message

from motor.motor_asyncio import AsyncIOMotorCollection


endpoints_db: AsyncIOMotorCollection = db.endpoints


async def check_valid_user(user_id: ObjectId):
    users_db = db.chat_users
    user = await users_db.count_documents({'_id': user_id})
    return bool(user)


"""
Small endpoints are these that dont have hard structure and multiple channels in
and for now these are only dms and group dms
/api/endpoints/channel/<id>

Big endpoints are parts of servers
/api/endpoints/servers/<id>/channels/<id>
"""


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

    async def send_message(
        self, author: ObjectId, content: str,
        files: List[str]=[], user_mentions=[],
        roles_mentions=[], channel_mentions=[]
        ):
        if author not in self.members:
            raise self.exc.NotGroupMember("User isn't a part of group")

        new_message = await Message.send_message(
            author, self._id, content, files, user_mentions
        )
        # setting out message as latest
        await endpoints_db.update_one({"_id": self._id}, {"$set": {"last_message": new_message._id}})
        self.last_message = new_message._id
        return new_message

    async def get_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember("User trying to get message in invalid group")

        # this may rise value error if no message found
        message = await Message.get_message(message_id, self._id)
        return message

    async def get_messages(self, requester: ObjectId, message_from: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember("User trying to get messages in invalid group")

        messages = await Message.get_messages(message_from, self._id)
        return messages

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


@dataclass
class DMchannel(TextEndpoint):
    async def create_invite(self, *args, **kwargs):
        raise self.exc.UnsupprotedMethod("Can't create invite to dm")

    @classmethod
    async def create_endpoint(cls, user_init: ObjectId, user_accept: ObjectId):
        if not await check_valid_user(user_accept):
            raise ValueError("User is invalid")

        existing_endpoint = await endpoints_db.count_documents({"$and": [
            {"members": [user_init, user_accept]},
            {"_type": {"$nin":
                [ChannelType.server_text, ChannelType.server_category, ChannelType.server_voice]
            }}
        ]})

        if existing_endpoint:
            raise ValueError("Endpoint already exists")

        new_dm = {
            "_type": ChannelType.dm,
            "members": [user_init, user_accept],
            "created_at": datetime.utcnow(),
            "last_message": None
        }
        id = await endpoints_db.insert_one(new_dm)
        new_dm["_id"] = id.inserted_id
        return cls(**new_dm)

    async def send_message(self, author: ObjectId, content: str, files: List[str]=[], **kwargs):
        await super().send_message(author, content, files)

class MetaEndpoint:
    @staticmethod
    async def get_small_endpoints_from_id(requester: ObjectId) -> Dict[ObjectId, TextEndpoint]:
        """
        Returns only non-specific channels like dms and groups
        """
        endpoints = {}
        small_endpoints_with_user = endpoints_db.find({"$and": [
            {"members": requester},
            {"_type": {"$nin":
                [ChannelType.server_text, ChannelType.server_category, ChannelType.server_voice]
            }}
        ]})

        async for endpoint in small_endpoints_with_user:
            if endpoint['_type'] == ChannelType.dm:
                endpoint = DMchannel(**endpoint)
                endpoints[endpoint._id] = endpoint

            elif endpoint['_type'] == ChannelType.group:
                # TODO: later change builder to group dms
                endpoint = DMchannel(**endpoint)
                endpoints[endpoint._id] = endpoint

        return endpoints

    @staticmethod
    async def get_small_endpoint(requester: ObjectId, endpoint_id: ObjectId):
        users_endpoint = await endpoints_db.find_one({"$and": [
            {"_id": endpoint_id},
            {"members": requester},
            {"_type": {"$nin":
                [ChannelType.server_text, ChannelType.server_category, ChannelType.server_voice]
            }}
        ]})
        if not users_endpoint:
            raise ValueError("Invalid endpoint")

        if users_endpoint['_type'] == ChannelType.dm:
            return DMchannel(**users_endpoint)

        elif users_endpoint['_type'] == ChannelType.group:
            # TODO: later change builder to group dms
            return DMchannel(**users_endpoint)

        raise ValueError("Invalid endpoint")
