from dataclasses import dataclass, field
from datetime import datetime
from random import choices
from string import ascii_letters, digits
from typing import List

from bson import ObjectId
from pymongo import UpdateOne

from app import db
from utils import exclude_keys

from .endpoint import MetaEndpoint
from .enums import Status
from .file_model import FileModel

users_db = db.chat_users

public_exclude = {
    "code": 0,
    "blocked": 0,
    "friends": 0,
    "pendings_outgoing": 0,
    "pendings_incoming": 0,
    "status": 0,
    "login": 0,
    "password": 0,
    "parent": 0,
    "token": 0
}
# TODO: add some method to reset passwords


@dataclass
class UserModel:
    _id: ObjectId
    nick: str
    created_at: datetime

    bot: bool = False
    token: str = field(default=None, repr=False)
    status: int = Status.offline
    text_status: str = ''
    code: str = field(default=None, repr=False)
    parent: int = field(default=None, repr=False)

    blocked: List[ObjectId] = field(default_factory=list, repr=False)
    friends: List[ObjectId] = field(default_factory=list, repr=False)

    pendings_outgoing: List[ObjectId] = field(default_factory=list, repr=False)
    pendings_incoming: List[ObjectId] = field(default_factory=list, repr=False)

    # ? Setters
    async def set_nick(self, new_nick):
        if len(new_nick) not in range(1, 25+1):
            raise ValueError("Invalid nickname")

        await users_db.update_one(
            {"_id": self._id},
            {"$set": {"nick": new_nick}}
        )
        self.nick = new_nick

    async def set_status(self, status: int):
        if status not in list(Status):
            raise ValueError("Wrong status")

        await users_db.update_one(
            {"_id": self._id},
            {"$set": {"status": status}}
        )
        self.status = status

    async def set_text_status(self, text_status: str):
        if len(text_status) > 256:
            raise ValueError("Too long status")

        await users_db.update_one(
            {"_id": self._id},
            {"$set": {"text_status": text_status}}
        )
        self.text_status = text_status

    async def set_friend_code(self, new_code: str):
        if len(new_code) not in range(3, 51):
            raise ValueError("Too long friend code")

        is_avaliable = await self._avaliable_friend_code(new_code)

        if not is_avaliable:
            raise ValueError("Code is already used")

        await users_db.update_one(
            {"_id": self._id},
            {"$set": {"code": new_code}}
        )
        self.code = new_code

    # ? Friends related
    async def send_friend_request(self, to_user_id: ObjectId):
        valid_user = await self._valid_user_id(to_user_id)

        if not valid_user:
            raise self.exc.InvalidUser("User isn't valid or is bot")

        is_blocked = await UserModel._check_blocked(to_user_id, self._id)

        if is_blocked:
            raise self.exc.InvalidUser("User blocked you")

        blocked_by_self = to_user_id in self.blocked

        if blocked_by_self:
            raise self.exc.InvalidUser("You blocked user yourself")

        in_other_relations = (
            to_user_id in self.pendings_incoming or
            to_user_id in self.pendings_outgoing or
            to_user_id in self.friends
        )

        if in_other_relations:
            raise self.exc.InvalidUser(
                "User is in some relations with you already"
            )

        await users_db.bulk_write([
            # Adding outgoing pending to user
            UpdateOne(
                {"_id": self._id},
                {"$push": {"pendings_outgoing": to_user_id}}
            ),
            # Adding incoming pending to other user
            UpdateOne(
                {"_id": to_user_id},
                {"$push": {"pendings_incoming": self._id}}
            )
        ])

    async def response_friend_request(self, user_id: ObjectId, confirm=True):
        if user_id not in self.pendings_incoming:
            raise self.exc.UserNotInGroup("User isn't in incoming pendings")

        operations = [
            UpdateOne(
                {'_id': user_id},
                {'$pull': {'pendings_outgoing': self._id}}
            ),
            UpdateOne(
                {'_id': self._id},
                {'$pull': {'pendings_incoming': user_id}}
            )
        ]

        if confirm:
            operations += [
                UpdateOne({'_id': self._id}, {'$push': {'friends': user_id}}),
                UpdateOne({'_id': user_id}, {'$push': {'friends': self._id}})
            ]

        await users_db.bulk_write(operations)

    async def cancel_friend_request(self, user_id: ObjectId):
        if user_id not in self.pendings_outgoing:
            raise self.exc.UserNotInGroup("User isn't in outgoing pendings")

        await users_db.bulk_write([
                # Deleting outgoing pending from list
                UpdateOne(
                    {"_id": self._id},
                    {"$pull": {"pendings_outgoing": user_id}}
                ),
                # Deleting our user from incoming pendings
                UpdateOne(
                    {"_id": user_id},
                    {"$pull": {"pendings_incoming": self._id}}
                )
            ])

    async def delete_friend(self, user_id: ObjectId):
        if user_id not in self.friends:
            raise self.exc.UserNotInGroup("User isn't a friend")

        await users_db.bulk_write([
            UpdateOne(
                {'_id': self._id},
                {'$pull': {'friends': user_id}}
            ),
            UpdateOne(
                {'_id': user_id},
                {'$pull': {'friends': self._id}}
            )
        ])

    async def get_friends(self, fetch_friends: list):
        users = users_db.find(
            {"_id": {"$in": list(fetch_friends)}},
            public_exclude
        )

        users_objects = []

        async for user in users:
            user = UserModel(**user)
            users_objects.append(user.public_dict)

        return users_objects

    # ? Blocked users related
    async def block_user(self, blocking: ObjectId):
        if (
            not await self._valid_user_id(blocking) or
            (blocking in self.blocked)
        ):
            raise self.exc.UserNotInGroup("User is already blocked or invalid")

        operations = [
            UpdateOne({'_id': self._id}, {'$push': {'blocked': blocking}})
        ]

        if blocking in self.pendings_incoming:
            operations += [
                UpdateOne(
                    {"_id": self._id},
                    {"$pull": {"pendings_outgoing": blocking}}
                ),
                UpdateOne(
                    {"_id": blocking},
                    {"$pull": {"pendings_incoming": self._id}}
                )
            ]

        if blocking in self.pendings_outgoing:
            operations += [
                UpdateOne(
                    {'_id': blocking},
                    {'$pull': {'pendings_outgoing': self._id}}
                ),
                UpdateOne(
                    {'_id': self._id},
                    {'$pull': {'pendings_incoming': blocking}}
                )
            ]

        if blocking in self.friends:
            operations += [
                UpdateOne(
                    {'_id': self._id},
                    {'$pull': {'friends': blocking}}
                ),
                UpdateOne(
                    {'_id': blocking},
                    {'$pull': {'friends': self._id}}
                )
            ]

        await users_db.bulk_write(operations)

    async def unblock_user(self, unblocking: ObjectId):
        if unblocking not in self.blocked:
            raise self.exc.UserNotInGroup("User isn't blocked")

        await users_db.update_one(
            {'_id': self._id},
            {'$pull': {'blocked': unblocking}}
        )

    async def get_blocked(self, fetch_blocked=set()):
        users = users_db.find(
            {"_id": {"$in": list(fetch_blocked)}},
            public_exclude
        )

        users_objects = []

        async for user in users:
            user = UserModel(**user)
            users_objects.append(user.public_dict)

        return users_objects

    # ? Endpoints related
    async def get_endpoints(self):
        endpoints = await MetaEndpoint.get_endpoints(self._id)
        return endpoints

    async def get_endpoint(self, endpoint_id: ObjectId):
        endpoint = await MetaEndpoint.get_endpoint(self._id, endpoint_id)
        return endpoint

    # ? Files related
    async def create_file(self, filename: str, systems_name: str):
        return await FileModel.create_file(self._id, filename, systems_name)

    @staticmethod
    async def get_file(file_id: ObjectId):
        return await FileModel.get_file(file_id)

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
        exclude_keys(output, [
            'token', 'connected', 'message_queue',
            "last_used_api_timestamp"
        ])
        return output

    @classmethod
    async def authorize(cls, login='', password='', token=''):
        user = None
        exclude = {
            'login': 0,
            'password': 0
        }
        if token:
            user = await users_db.find_one(
                {'token': token},
                exclude
            )

        elif login and password:
            user = await users_db.find_one(
                {'login': login, 'password': password},
                exclude
            )

        else:
            raise ValueError("Not enough auth info")

        if not user:
            raise cls.exc.InvalidUser("No such user")

        return cls(**user)

    @classmethod
    async def from_id(cls, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        user = await users_db.find_one(
            {'_id': user_id},
            public_exclude
        )

        if not user:
            raise cls.exc.InvalidUser("User id doesn't exists")

        return cls(**user)

    @classmethod
    async def registrate(cls, nick: str, login: str, password: str):
        new_user = {
            'bot': False,
            'nick': nick,
            'login': login,
            'password': password,
            'status': Status.online,
            'token': cls.generate_token(),
            'blocked': [],
            'friends': [],
            'pendings_outgoing': [],
            'pendings_incoming': [],
            'created_at': datetime.utcnow()
        }

        if await users_db.find_one({'login': login}):
            raise ValueError("Disallowed registration")

        inserted = await users_db.insert_one(new_user)
        new_user['_id'] = inserted.inserted_id
        exclude_keys(new_user, ['password', 'login'])
        return cls(**new_user)

    @classmethod
    async def registrate_bot(cls):
        # TODO: finish this method later
        ...

    @staticmethod
    def generate_token() -> str:
        # TODO: choose some other way of generating tokens
        letters_set = digits + ascii_letters
        token = ''.join(choices(letters_set, k=64))
        return token

    @staticmethod
    async def _avaliable_friend_code(code: str) -> bool:
        same_codes = await users_db.count_documents(
            {"code": code}
        )
        return not bool(same_codes)

    @staticmethod
    async def _friend_code_owner(code):
        user_id = await users_db.find_one(
            {"code": code},
            {"_id": 1, "total": 1}
        )
        return user_id.get('_id')

    @staticmethod
    async def _valid_user_id(user_id: ObjectId, bot=False) -> bool:
        user = await users_db.count_documents(
                {
                    "$and":
                    [{'_id': user_id}, {'bot': bot}]
                }
            )
        return bool(user)

    @staticmethod
    async def _check_blocked(
        check_user_id: ObjectId,
        is_blocked: ObjectId
    ) -> bool:
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

    class exc:
        class UserNotInGroup(ValueError):
            ...

        class InvalidUser(ValueError):
            ...
