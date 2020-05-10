from app import client

from .invites import Invite
from .messages import Message
from .enums import ChannelType

from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

db = client.endpoints


class EndpointException(Exception): ...
class NotGroupMember(EndpointException): ...
class NoPermissionForAction(EndpointException): ...



@dataclass
class DMChannel:
    _id: ObjectId
    _type: int = ChannelType.dm
    members: List[ObjectId] = []
    last_message: ObjectId = None

    @classmethod
    def create_endpoint(cls, user_init: str, user_accept: str):
        # likely raises bson.errors.InvalidId
        user_init = ObjectId(user_init)
        user_accept = ObjectId(user_accept)

        if not (
            cls.check_valid_user(user_accept) and
            cls.check_valid_user(user_init)
            ):
            raise ValueError("One of two users is invalid")

        new_dm = {
            "_type": ChannelType.dm,
            "members": [user_init, user_accept],
            "created_at": datetime.utcnow(),
            "last_message": None
        }
        id = db.insert_one(new_dm).inserted_id

        return cls(_id = id, **new_dm)

    @staticmethod
    def check_valid_user(user_id: ObjectId):
        users_db = client.chat_users
        user = users_db.count_documents({'_id': user_id})
        return bool(user)

    def send_message(self, author: str, content: str, *files: List[str]):
        # likely raises bson.errors.InvalidId
        author_id = ObjectId(author)

        if author_id not in self.members:
            raise NotGroupMember("User trying to send message in invalid group")

        new_message = Message.send_message(
            author, self._id, content, *files
        )
        return new_message

    def edit_message(self, requester: str, message_id: str, content: str):
        # likely raises bson.errors.InvalidId
        author_id = ObjectId(requester)

        if author_id not in self.members:
            raise NotGroupMember("User trying to edit message in invalid group")

        return Message.edit_message(author_id, message_id, content)

    def delete_message(self, requester: str, message_id: str):
        # likely raises bson.errors.InvalidId
        requester = ObjectId(requester)

        if requester not in self.members:
            raise NotGroupMember("User trying to edit message in invalid group")

        return Message.delete_message(requester, message_id)

    def set_message_pin(self, requester: str, message_id: str, pin: bool):
        # likely raises bson.errors.InvalidId
        author_id = ObjectId(requester)

        if author_id not in self.members:
            raise NotGroupMember("User trying to edit message in invalid group")

        return Message.set_message_pin(author_id, message_id, pin)


@dataclass
class GroupDMChannel:
    _id: ObjectId
    _type: int = ChannelType.group
    name: str
    owner: ObjectId
    nsfw: bool = False
    last_message: ObjectId = None
    members: List[ObjectId] = []
    created_at: datetime

    @staticmethod
    def create_endpoint():
        pass

    def send_message(self): ...

    def set_group_name(self): ...

    def set_group_topic(self): ...

    def set_group_nsfw(self): ...

    def get_invites(self): ...

    def create_invite(self): ...

    def delete_invite(self): ...

    def kick_user(self): ...
