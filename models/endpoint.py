from bson import ObjectId
from bson import errors as bson_errors
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass

from app import db
from .enums import ChannelType
from .messages import Message

endpoints_db = db.endpoints


async def validate_user(user_id: ObjectId) -> bool:
    # This function is there to create valid endpoints
    # We need endpoints file in user module so just copypate
    users_db = db.chat_users
    user = await users_db.count_documents({'_id': user_id})
    return bool(user)


async def _check_blocked(
    check_user_id: ObjectId,
    is_blocked: ObjectId
) -> bool:
    users_db = db.chat_users
    is_blocked = await users_db.count_documents(
        {
            "$and":
            [
                {"_id": check_user_id},
                {"blocked": {"$in": [is_blocked]}}
            ]
        }
    )
    return bool(is_blocked)


@dataclass
class TextEndpoint:
    _id: ObjectId
    _type: int
    members: List[ObjectId]
    created_at: datetime
    last_message: ObjectId = None
    last_pinned: ObjectId = None

    @classmethod
    async def create_endpoint(cls, **kwargs):
        raise NotImplementedError()

    async def create_invite(self):
        raise NotImplementedError()

    async def send_message(
        self,
        author: ObjectId, content: str, files=[],
        **_
    ) -> Message:
        if author not in self.members:
            raise self.exc.NotGroupMember("User isn't a part of group")

        files_ids = []
        for _file in files:
            try:
                _file = ObjectId(_file)
                files_ids.append(_file)

            except bson_errors.InvalidId:
                continue

        msg = await Message.send_message(
            author, self._id, content,
            files_ids
        )

        await endpoints_db.update_one(
            {"_id": self._id},
            {"$set": {"last_message": msg._id}}
        )
        self.last_message = msg._id

        return msg

    async def edit_message(
        self,
        requester: ObjectId,
        message_id: ObjectId,
        content: str
    ):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to edit message in invalid group"
            )

        if not content:
            raise ValueError("Should give at least some content")

        return await Message.edit_message(requester, message_id, content)

    async def pin_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to pin message in invalid group"
            )

        result = await Message.pin_message(requester, message_id)
        if result:
            await endpoints_db.update_one(
                {"_id": self._id},
                {"$set": {"last_pinned": message_id}}
            )

        return result

    async def unpin_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to unpin message in invalid group"
            )

        return await Message.unpin_message(requester, message_id)

    async def get_pinned_messages(self, requester: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch pinned messages in invalid group"
            )

        pinned_msgs = await Message.batch_pinned(self.last_pinned, self._id)
        return pinned_msgs

    async def get_pinned_messages_from(
        self,
        requester: ObjectId,
        message_id: ObjectId
    ):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch pinned messages in invalid group"
            )

        pinned_msgs = await Message.batch_pinned(message_id, self._id)
        return pinned_msgs

    async def get_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch message in invalid group"
            )

        msg = await Message.get_message(message_id, self._id)

        if not msg:
            raise ValueError("No such message")

        return msg

    async def get_messages(self, requester: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch messages in invalid group"
            )

        msgs = await Message.get_messages_from(self.last_message, self._id)
        return msgs

    async def get_messages_from(
        self,
        requester: ObjectId,
        from_message: ObjectId
    ):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch messages in invalid group"
            )

        msgs = await Message.get_messages_from(from_message, self._id)
        return msgs

    async def get_messages_after(
        self,
        requester: ObjectId,
        after_message: ObjectId
    ):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch messages in invalid group"
            )

        msgs = await Message.get_messages_after(after_message, self._id)
        return msgs

    async def delete_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to delete message in invalid group"
            )

        return Message.delete_message(requester, message_id, self._id)

    async def force_delete_message(
        self,
        requester: ObjectId,
        message_id: ObjectId
    ):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to delete message in invalid group"
            )

        # ! Check permissions before deleting
        return Message.force_delete(message_id, self._id)

    class exc:
        class EndpointException(Exception):
            ...

        class NotGroupMember(EndpointException):
            ...

        class NoPermission(EndpointException):
            ...


@dataclass
class DMChannel(TextEndpoint):
    @classmethod
    async def create_endpoint(cls, user_init: ObjectId, user_accept: ObjectId):
        if not await validate_user(user_accept):
            raise ValueError("User is invalid")

        blocked_eachother = (
            await _check_blocked(user_accept, user_init) or
            await _check_blocked(user_init, user_accept)
        )

        if blocked_eachother:
            raise ValueError(
                "Sorry, but one of users blocked each other and cant start dm"
            )

        existing_endpoint = await endpoints_db.count_documents({"$and": [
            {"members": [user_init, user_accept]},
            {"_type": {
                "$nin":
                [
                    ChannelType.group,
                    ChannelType.server_text,
                    ChannelType.server_category,
                    ChannelType.server_voice
                ]
            }}
        ]})

        if existing_endpoint:
            raise ValueError("Endpoint already exists")

        new_dm = {
            "_type": ChannelType.dm,
            "members": [user_init, user_accept],
            "created_at": datetime.utcnow(),
            "last_message": None,
            "last_pinned": None
        }
        id = await endpoints_db.insert_one(new_dm)
        new_dm["_id"] = id.inserted_id

        return cls(**new_dm)

    async def send_message(
        self,
        author: ObjectId, content: str, files: List[str],
        mentions: List[str] = [], **_
    ):

        blocked_eachother = (
            await _check_blocked(*self.members) or
            await _check_blocked(*self.members)
        )

        if blocked_eachother:
            raise self.exc.NoPermission("Channel blocked")

        await super().send_message(author, content, files)

    async def create_invite(self, *args, **kwargs):
        raise NotImplementedError()

    async def force_delete_message(self, *args, **kwargs):
        raise NotImplementedError()


class MetaEndpoint:
    @staticmethod
    async def get_endpoints(requester: ObjectId) -> Dict[
        ObjectId, TextEndpoint
    ]:
        dict_endpoints = {}
        endpoints = endpoints_db.find({"$and": [
            {"members": {"$in": [requester]}},
            {"_type": {
                "$nin":
                [
                    ChannelType.server_text,
                    ChannelType.server_category,
                    ChannelType.server_voice
                ]
            }}
        ]})

        async for endpoint in endpoints:
            if endpoint['_type'] == ChannelType.dm:
                endpoint = DMChannel(**endpoint)
                dict_endpoints[endpoint._id] = endpoint

        return dict_endpoints

    @staticmethod
    async def get_endpoint(
        requester: ObjectId,
        endpoint_id: ObjectId
    ) -> TextEndpoint:
        users_endpoint = await endpoints_db.find_one({"$and": [
            {"_id": endpoint_id},
            {"members": {"$in": [requester]}},
            {"_type": {
                "$nin":
                [
                    ChannelType.server_text,
                    ChannelType.server_category,
                    ChannelType.server_voice
                ]
            }}
        ]})

        if not users_endpoint:
            raise ValueError("Invalid endpoint")

        if users_endpoint['_type'] == ChannelType.dm:
            return DMChannel(**users_endpoint)

        raise ValueError("Invalid endpoint")
