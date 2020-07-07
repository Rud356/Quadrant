from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from bson import SON, ObjectId

from app import connected_users, db

from .enums import ChannelType
from .invites_model import Invite
from .message_model import MessageModel

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
    if check_user_id not in connected_users:
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

    else:
        user = connected_users.get(check_user_id)
        is_blocked = is_blocked in user.blocked

    return bool(is_blocked)


@dataclass
class TextEndpoint:
    _id: ObjectId
    _type: int
    members: List[ObjectId]
    created_at: datetime
    last_message: ObjectId = None
    last_pinned: ObjectId = None

    async def send_message(
        self,
        author: ObjectId, content: str, files=[],
        **_
    ) -> MessageModel:
        if author not in self.members:
            raise self.exc.NotGroupMember("User isn't a part of group")

        msg = await MessageModel.send_message(
            author, self._id, content,
            files
        )

        await endpoints_db.update_one(
            {"_id": self._id},
            {"$set": {"last_message": msg._id}}
        )
        self.last_message = msg._id

        return msg

    async def get_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch message in invalid group"
            )

        msg = await MessageModel.get_message(message_id, self._id)

        if not msg:
            raise ValueError("No such message")

        return msg

    async def get_messages(self, requester: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to fetch messages in invalid group"
            )

        msgs = await MessageModel.get_messages_from_including(
            self.last_message,
            self._id
        )
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

        msgs = await MessageModel.get_messages_from(from_message, self._id)
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

        msgs = await MessageModel.get_messages_after(after_message, self._id)
        return msgs

    async def delete_message(self, requester: ObjectId, message_id: ObjectId):
        if requester not in self.members:
            raise self.exc.NotGroupMember(
                "User trying to delete message in invalid group"
            )

        return MessageModel.delete_message(requester, message_id, self._id)

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
        return await MessageModel.force_delete(message_id, self._id)

    @classmethod
    async def create_endpoint(cls, **kwargs):
        raise NotImplementedError()

    async def create_invite(self):
        raise NotImplementedError()


    async def accept_invite(self):
        raise NotImplementedError()

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

        blocked_each_other = (
            await _check_blocked(user_accept, user_init) or
            await _check_blocked(user_init, user_accept)
        )

        if blocked_each_other:
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
            await _check_blocked(self.members[0], self.members[1]) or
            await _check_blocked(self.members[1], self.members[0])
        )

        if blocked_eachother:
            raise self.exc.NoPermission("Channel blocked")

        return await super().send_message(author, content, files)

    async def force_delete_message(self, *args, **kwargs):
        raise NotImplementedError()


@dataclass
class GroupDM(TextEndpoint):
    title: str = ''
    owner: ObjectId = None
    owner_edits_only: bool = True

    @classmethod
    async def create_endpoint(cls, creator: ObjectId, title: str):
        if len(title) not in range(1, 51):
            raise ValueError("Too long title")

        endpoint = {
            "_type": ChannelType.group,
            "members": [creator],
            "owner": creator,
            "title": title,
            "owner_edits_only": True,
            "created_at": datetime.utcnow(),
            "last_message": None,
            "last_pinned": None
        }
        id = await endpoints_db.insert_one(endpoint)
        endpoint["_id"] = id.inserted_id

        return cls(**endpoint)

    @staticmethod
    async def accept_invite(acceptor: ObjectId, code: str):
        invite: Invite = await Invite.get_invite(code)
        await endpoints_db.update_one(
            {'_id': invite.endpoint}, {"$push": {"members": acceptor}}
        )
        return invite.endpoint

    async def create_invite(self, creator: ObjectId, user_limit: int, expires_at: int):
        if creator != self.owner:
            raise self.exc.NoPermission()

        new_invite = await Invite.create_invite(
            self._id, creator, user_limit, expires_at
        )

        return new_invite

    async def delete_invite(self, code: str):
        return await Invite.delete_invite(code, self._id)

    async def force_delete_message(
        self,
        requester: ObjectId,
        message_id: ObjectId
    ):
        if requester != self.owner:
            raise self.exc.NoPermission()

        return await super().force_delete_message(
            requester, message_id
        )

    async def remove_user(self, user: ObjectId):
        return await endpoints_db.update_one(
            {'_id': self._id}, {"$pull": {"members": user}}
        )


class MetaEndpoint:
    @staticmethod
    async def get_endpoints_ids(requester: ObjectId) -> Dict[
        ObjectId, TextEndpoint
    ]:
        list_endpoints = []
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
        ]},
        {"_id": 1}
        )

        async for endpoint in endpoints:
            list_endpoints.append(endpoint['_id'])

        return list_endpoints

    @staticmethod
    async def aggregation_paged_endpoints(requester: ObjectId, page: int = 0) -> Dict[
        ObjectId, TextEndpoint
    ]:
        pipeline = [
            {"$match": {"$in": [requester]}},
            {"$sort": SON([("last_message", -1), ("_id", -1)])},
            {"$skip": page*100},
            {"$limit": 100}
        ]

        cursor = endpoints_db.aggregate(pipeline)
        endpoints = {}
        async for endpoint in cursor:
            endpoints[str(endpoint['_id'])] = endpoint

        return endpoints

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
            dict_endpoints[str(endpoint["_id"])] = endpoint
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

        if users_endpoint['_type'] == ChannelType.group:
            return GroupDM(**users_endpoint)

        raise ValueError("Invalid endpoint")
