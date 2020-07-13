from asyncio import get_running_loop
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import pbkdf2_hmac, sha3_256
from random import choices, randint
from secrets import randbits
from string import ascii_letters, digits
from time import time
from typing import List

from bson import SON, ObjectId
from pymongo import UpdateOne

from app import db
from utils import exclude_keys, string_strips

from .caches import authorization_cache
from .endpoint_model import MetaEndpoint
from .enums import Status

users_db = db.chat_users

EXCLUDE_PUBLIC = {
    "friend_code": 0,
    "salt": 0,
    "token": 0,
    "login": 0,
    "password": 0,
    "status": 0,
    "blocked": 0,
    "friends": 0,
    "pendings_outgoing": 0,
    "pendings_incoming": 0,
}


@dataclass
class UserModel:
    _id: ObjectId
    nick: str
    created_at: datetime

    bot: bool = False
    deleted: bool = False
    token: str = field(default=None, repr=False)
    status: int = Status.offline
    text_status: str = ''
    friend_code: str = field(default=None, repr=False)
    parent: int = field(default=None, repr=False)

    blocked: List[ObjectId] = field(default_factory=list, repr=False)
    friends: List[ObjectId] = field(default_factory=list, repr=False)

    pendings_outgoing: List[ObjectId] = field(default_factory=list, repr=False)
    pendings_incoming: List[ObjectId] = field(default_factory=list, repr=False)


    # ? Dangerouts methods
    async def update_token(self):
        # Updating token of user
        # Leading to log out on all devices
        new_token = self.generate_token()
        await users_db.update_one(
            {'_id': self._id},
            {'$set': {'token': new_token}}
        )
        self.token = new_token
        return new_token

    async def delete_user(self):
        bulk_user_removing = (
            UpdateOne(
                {"_id": self._id},
                {"$unset": {
                    "token": "",
                    "status": "",
                    "text_status": "",
                    "friend_code": "",
                    "parent": "",
                    "blocked": "",
                    "friends": "",
                    "pendings_outgoing": "",
                    "pendings_incoming": "",
                }}
            ),
            UpdateOne(
                {"_id": self._id},
                {"$set": {"deleted": True}}
            )
        )

        await users_db.bulk_write(bulk_user_removing)

    # ? Setters
    async def update(
        self, *,
        nick: str = None, status: int = None,
        text_status: str = None, friend_code: str = None,
        **_
    ):
        if any((nick, status, text_status, friend_code and not self.bot)):
            actions = []
            update = {"_id": self._id}

            if nick:
                nick = string_strips(nick)
                actions.append(
                    UpdateOne(
                        {"_id": self._id},
                        {"$set": {"nick": nick}}
                    )
                )

                update["nick"] = nick
                self.nick = nick

            if status:
                actions.append(
                    UpdateOne(
                        {"_id": self._id},
                        {"$set": {"status": status}}
                    )
                )

                update["status"] = status
                self.status = status

            if text_status:
                text_status = string_strips(text_status)
                actions.append(
                    UpdateOne(
                        {"_id": self._id},
                        {"$set": {"text_status": status}}
                    )
                )

                update["text_status"] = text_status
                self.text_status = text_status

            if await self._avaliable_friend_code(friend_code) and not self.bot:
                friend_code = string_strips(friend_code)
                actions.append(
                    UpdateOne(
                        {"_id": self._id},
                        {"$set": {"friend_code": friend_code}}
                    )
                )

                update["friend_code"] = friend_code
                self.friend_code = friend_code

            await users_db.bulk_write(actions)
            return update

        else:
            raise ValueError("No values given")

    # ? Friends related
    async def send_friend_request(self, to_user_id: ObjectId):
        if self.bot:
            raise self.exc.UnavailableForBots()

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
        if self.bot:
            raise self.exc.UnavailableForBots()

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
        if self.bot:
            raise self.exc.UnavailableForBots()

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
        if self.bot:
            raise self.exc.UnavailableForBots()

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

    def aggregation_paged_outgoing_requests(self, page: int = 0):
        # Returning only cursor to iterate through to get outgoing pendings
        pipeline = [
            {"$match": {"$in": self.pendings_outgoing}},
            {"$sort": SON([("name", -1), ("_id", -1)])},
            {"$unset": EXCLUDE_PUBLIC},
            {"$skip": page*100},
            {"$limit": 100}
        ]
        cursor = users_db.aggregate(pipeline)
        return cursor

    def aggregation_paged_incoming_requests(self, page: int = 0):
        # Returning only cursor to iterate through to get incoming pendings
        pipeline = [
            {"$match": {"$in": self.pendings_incoming}},
            {"$sort": SON([("name", -1), ("_id", -1)])},
            {"$unset": EXCLUDE_PUBLIC},
            {"$skip": page*100},
            {"$limit": 100}
        ]
        cursor = users_db.aggregate(pipeline)
        return cursor

    def aggregation_paged_friends(self, page: int = 0):
        # Returning only cursor to iterate through to get friends
        pipeline = [
            {"$match": {"$in": self.friends}},
            {"$sort": SON([("name", -1), ("_id", -1)])},
            {"$unset": EXCLUDE_PUBLIC},
            {"$skip": page*100},
            {"$limit": 100}
        ]
        cursor = users_db.aggregate(pipeline)
        return cursor

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

    def aggregation_paged_blocked(self, page: int = 0):
        # Returning only cursor to iterate through to get blocked
        pipeline = [
            {"$match": {"$in": self.blocked}},
            {"$sort": SON([("name", -1), ("_id", -1)])},
            {"$unset": EXCLUDE_PUBLIC},
            {"$skip": page*100},
            {"$limit": 100}
        ]
        cursor = users_db.aggregate(pipeline)
        return cursor

    # ? Endpoints related
    # TODO: write aggregation to gather latest chats
    # If user doesn't have endpoint that just recieved msg in cache
    # he have to query it
    async def get_endpoints(self):
        endpoints = await MetaEndpoint.get_endpoints(self._id)
        return endpoints

    async def get_endpoints_ids(self):
        endpoints = await MetaEndpoint.get_endpoints_ids(self._id)
        return endpoints

    async def get_endpoint(self, endpoint_id: ObjectId):
        endpoint = await MetaEndpoint.get_endpoint(self._id, endpoint_id)
        return endpoint

    async def get_bots(self):
        users_bots = await users_db.find({'parent': self._id})
        bots = []

        async for bot in users_bots:
            bot = UserModel(**bot)
            bot_dict = bot.public_dict
            bot_dict.update({'token': bot.token})
            bots.append(bot_dict)

        return bots

    @property
    def public_dict(self):
        user_dict = {
            '_id': self._id,
            "status": self.status,
            "text_status": self.text_status,
            "bot": self.bot,
            "nick": self.nick,
            "created_at": self.created_at,
        }

        if self.deleted:
            user_dict['deleted'] = True

        return user_dict

    @property
    def private_dict(self):
        # making sure that our object is new one
        output = dict(self.__dict__)
        exclude_keys(output, [
            'token', 'connected', 'message_queue',
            "last_used_api_timestamp", "deleted",
            'kill_websockets'
        ])
        return output

    @classmethod
    async def authorize(cls, login='', password='', token=''):
        user = None
        exclude = {
            'login': 0,
            'password': 0,
            'salt': 0
        }

        if token:
            user = await users_db.find_one(
                {'token': token},
                exclude
            )

        elif login and password:
            login = sha3_256(login.encode())
            login = login.hexdigest()

            salt = await cls._get_salt_hashed_login(login)
            if not salt:
                raise ValueError("Invalid login")

            password = await UserModel._hash_password_with_salt(password=password, salt=salt)
            password = password.hex()

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
            EXCLUDE_PUBLIC
        )

        if not user:
            raise cls.exc.InvalidUser("User id doesn't exists")

        return cls(**user)

    @classmethod
    async def registrate(cls, nick: str, login: str, password: str):
        salt = cls.generate_salt()
        password = await cls._hash_password_with_salt(password.encode(), salt.encode())

        password = password.hex()
        login = sha3_256(login.encode()).hexdigest()

        new_user = {
            'bot': False,
            'salt': salt,
            'nick': nick,
            'login': login,
            'password': password,
            'status': Status.online,
            'token': cls.generate_token(),
            'blocked': [],
            'friends': [],
            'pendings_outgoing': [],
            'pendings_incoming': [],
            'created_at': datetime.utcnow(),
        }

        if await users_db.find_one({'login': login}):
            raise ValueError("Disallowed registration")

        inserted = await users_db.insert_one(new_user)
        new_user['_id'] = inserted.inserted_id
        exclude_keys(new_user, ['password', 'login', 'salt'])

        return cls(**new_user)

    @classmethod
    async def registrate_bot(cls, nick: str, parent: ObjectId):
        has_number_of_bots = await users_db.count_documents(
            {
                "$and":
                [
                    {'parent': parent},
                    {'deleted': {'$exists': False}}
                ]
            }
        )

        if has_number_of_bots > 20:
            raise ValueError("Too many bots")

        new_user = {
            'bot': True,
            'nick': nick,
            'parent': parent,
            'status': Status.online,
            'token': cls.generate_token(),
            'blocked': [],
            'friends': [],
            'pendings_outgoing': [],
            'pendings_incoming': [],
            'created_at': datetime.utcnow(),
        }

        inserted = await users_db.insert_one(new_user)
        new_user['_id'] = inserted.inserted_id

        return cls(**new_user)

    @staticmethod
    def generate_token() -> str:
        letters_set = digits + ascii_letters
        token = hex(int(time())) + ''.join(
            choices(letters_set, k=randint(50, 64))
        )
        return token

    @staticmethod
    def generate_salt(size=128):
        salt_origin = randbits(size)
        hashed = sha3_256(salt_origin)
        return hashed.hexdigest()

    @staticmethod
    @authorization_cache.cache_login_salt
    async def _get_salt_hashed_login(login: str):
        salt = await users_db.find_one(
            {"login": login},
            {"salt": 1}
        )
        return salt['salt']

    @staticmethod
    @authorization_cache.cache_passwords
    async def _hash_password_with_salt(password: str, salt: bytes):
        loop = get_running_loop()
        password = await loop.run_in_executor(
            None,
            pbkdf2_hmac,
            'sha3_256', password.encode(), salt.encode(), 100000
        )
        return password

    @staticmethod
    async def _avaliable_friend_code(friend_code: str) -> bool:
        same_friend_codes = await users_db.count_documents(
            {"friend_code": friend_code}
        )
        return not bool(same_friend_codes)

    @staticmethod
    async def _friend_code_owner(friend_code):
        user_id = await users_db.find_one(
            {"friend_code": friend_code},
            {"_id": 1, "total": 1}
        )
        return user_id.get('_id')

    @staticmethod
    async def _valid_user_id(user_id: ObjectId, bot=False) -> bool:
        user = await users_db.count_documents(
            {
                "$and":
                [
                    {'_id': user_id},
                    {'bot': bot},
                    {'deleted': {'$exists': False}}
                ]
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

        class UnavailableForBots(ValueError):
            ...
