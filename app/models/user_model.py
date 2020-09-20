from __future__ import annotations

from typing import List
from datetime import datetime
from dataclasses import dataclass, field
from hashlib import sha256

from .collections import users_db
from .utils import (
    EXCLUDE_PUBLIC, EXCLUDE_LOADING, calculate_password_hash,
    generate_salt, generate_token
)
from .enums import UserStatus

from pymongo import UpdateOne
from bson import ObjectId


@dataclass
class User:
    _id: ObjectId
    nick: str
    created_at: datetime

    token: str = field(repr=False)
    login: str = field(default="", repr=False)
    password: str = field(default="", repr=False)

    status: int = field(default=UserStatus.offline)
    text_status: str = field(default="", repr=False)
    friend_code: str = field(default="", repr=False)
    bot: bool = field(default=True)
    parent_id: ObjectId = field(default=None)
    deleted: bool = field(default=True)

    async def parent(self) -> User:
        if self.bot:
            # TODO: complete
            return await self.get(self.parent_id)

        else:
            raise self.exc.UserIsNotBot()

    async def bots(self) -> List[User]:
        bots = users_db.find(
            {
                "$and": [
                    {"parent_id": self._id},
                    {"deleted": {'$exists': False}}
                ],
            },
            EXCLUDE_LOADING
        )

        return [User(**bot) async for bot in bots]

    async def update_token(self):
        self.token = generate_token()
        await users_db.update_one(
            {"_id": self._id},
            {"$set": {"token": self.token}}
        )

        return self.token

    async def delete(self):
        bulk_user_removing = [
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
                    "outgoing_friend_requests": "",
                    "incoming_friend_requests": "",
                }}
            ),
            UpdateOne(
                {"_id": self._id},
                {"$set": {"deleted": True}}
            )
        ]

        await users_db.bulk_write(bulk_user_removing)

    async def update(
            self, *, nick: str = None, status: int = None,
            text_status: str = None, friend_code: str = None, **_
    ):
        if not any((nick, status, text_status, friend_code)):
            raise self.exc.NoUpdateFieldsProvided("No updatable fields provided")

        functions_and_params = zip(
            (
                self.update_nick, self.update_status,
                self.update_text_status, self.update_friend_code
            ),
            (nick, status, text_status, friend_code),
            ('nick', 'status', 'text_status', 'friend_code')
        )

        functions_and_params = filter(
            lambda f, v, n: v is None,
            functions_and_params
        )
        updated_fields = {}
        updates = []
        for func, arg, arg_name in functions_and_params:
            try:
                update_statement = func(arg)
                updates.append(update_statement)
                updated_fields[arg_name] = arg

            except (self.exc.InvalidFriendCode, self.exc.InvalidValueProvided):
                continue

        if not len(updates):
            raise self.exc.NoUpdateFieldsProvided()

        await users_db.bulk_write(updates)
        return updated_fields

    async def update_password(self, password: str):
        if self.bot:
            raise self.exc.UserIsBot()

        # TODO: validate password

        salt = generate_salt()
        self.password = await calculate_password_hash(password, salt)

        await users_db.update_one(
            {"_id": self._id},
            {"$set": {"salt": salt, "password": self.password}}
        )

    def update_nick(self, new_nick: str) -> UpdateOne:
        # TODO: validate nick
        self.nick = new_nick
        return UpdateOne({"_id": self._id}, {"$set": {"nick": new_nick}})

    def update_status(self, status: int) -> UpdateOne:
        if status in tuple(UserStatus):
            raise self.exc.InvalidValueProvided(f"Status value {status} is invalid")

        self.status = status
        return UpdateOne({"_id": self._id}, {"$set": {"status": status}})

    def update_text_status(self, text_status: str) -> UpdateOne:
        # TODO: validate nick
        self.text_status = text_status
        return UpdateOne({"_id": self._id}, {"$set": {"text_status": text_status}})

    def update_friend_code(self, friend_code: str) -> UpdateOne:
        if self.bot:
            raise self.exc.UserIsBot()

        try:
            self.friend_code_owner_id(friend_code)

        except ValueError:
            pass

        else:
            raise self.exc.InvalidFriendCode()

        self.friend_code = friend_code
        return UpdateOne({"_id": self._id}, {"$set": {"friend_code": friend_code}})

    async def is_user_blocked(self, other_user_id: ObjectId) -> bool:
        is_blocked = await users_db.count_documents(
            {
                "$and":
                    [
                        {"_id": {"$in": [other_user_id, self._id]}},
                        {"blocked": {"$in": [other_user_id, self._id]}}
                    ]
            }
        )
        return bool(is_blocked)

    async def is_in_relationships_with(self, other_user_id: ObjectId):
        is_in_relationships = await users_db.count_documents(
            {
                "$and":
                    [
                        {"_id": {"$in": [other_user_id, self._id]}},
                        {
                            "$or": [
                                {"blocked": {"$in": [other_user_id, self._id]}},
                                {"friends": {"$in": [other_user_id, self._id]}},
                                {"incoming_friend_requests": {"$in": [other_user_id, self._id]}},
                                {"outgoing_friend_requests": {"$in": [other_user_id, self._id]}}
                            ]
                        }
                    ]
            }
        )

        return bool(is_in_relationships)

    async def send_friend_request(self, user_id: ObjectId):
        if self.bot:
            raise self.exc.UserIsBot()

        valid_user = await self.valid_user_id(user_id)

        if not valid_user:
            raise self.exc.UserNotFound()

        if await self.is_in_relationships_with(user_id):
            raise self.exc.AlreadyInRelationships()

        await users_db.bulk_write([
            # Adding outgoing pending to user
            UpdateOne(
                {"_id": self._id},
                {"$push": {"outgoing_friend_requests": user_id}}
            ),
            # Adding incoming pending to other user
            UpdateOne(
                {"_id": user_id},
                {"$push": {"incoming_friend_requests": self._id}}
            )
        ])

    @classmethod
    async def get(cls, user_id: ObjectId):
        user = await users_db.find_one(
            {
                "$and": [
                    {"_id": user_id},
                    {"deleted": {'$exists': False}}
                ]
            },
            EXCLUDE_PUBLIC
        )

        if user is None:
            raise cls.exc.UserNotFound()

        return cls(**user)

    @classmethod
    async def authorize(cls, login: str = '', password: str = '', token: str = ''):
        if token:
            return await cls.token_authorization(token)

        elif login and password:
            return await cls.password_authorization(login, password)

        else:
            raise cls.exc.NotEnoughAuthCredentials()

    @classmethod
    async def token_authorization(cls, token: str):
        user = await users_db.find_one(
            {'token': token, 'deleted': {'$ne': True}},
            EXCLUDE_LOADING
        )

        if not user:
            raise cls.exc.UserNotFound()

        return cls(**user)

    @classmethod
    async def password_authorization(cls, login: str, password: str):
        login = sha256(login.encode()).hexdigest()
        salt = await cls.get_salt_by_login(login)
        password = calculate_password_hash(password, salt)

        user = await users_db.find_one(
            {
                'login': login, 'password': password,
                'deleted': {'$ne': True}
            },
            EXCLUDE_LOADING
        )

        if not user:
            raise cls.exc.UserNotFound()

        return cls(**user)

    @classmethod
    async def register(cls, nick: str, login: str, password: str):
        # TODO: validate login, nick and password
        salt = generate_salt()
        token = generate_token()
        login = sha256(login.encode()).hexdigest()
        password = await calculate_password_hash(password, salt)

        if await cls.is_login_taken(login):
            raise cls.exc.UserAlreadyExists("Already")

        user = {
            "bot": False, "salt": salt, "nick": nick,
            "login": login, "password": password, "token": token,
            "status": UserStatus.online,
            "blocked": [], "friends": [],
            "incoming_friend_requests": [],
            "outgoing_friend_requests": [],
            "created_at": datetime.utcnow()
        }

        _id = (await users_db.insert_one(user)).inserted_id
        user['_id'] = _id
        return cls(**user)

    @classmethod
    async def register_bot(cls, nick: str, parent: User):
        # TODO: validate login, nick and password
        has_number_of_bots = await users_db.count_documents(
            {
                "$and":
                    [
                        {'parent': parent},
                        {'deleted': {'$exists': False}}
                    ]
            },
            EXCLUDE_LOADING
        )

        if parent.bot:
            raise cls.exc.UserIsBot()

        if has_number_of_bots > 20:
            raise ValueError("Too many bots")

        user = {
            "bot": False, "nick": nick,
            "token": generate_token(),
            "status": UserStatus.online,
            "created_at": datetime.utcnow()
        }

        _id = (await users_db.insert_one(user)).inserted_id
        user['_id'] = _id
        return cls(**user)

    @staticmethod
    async def user_exists(user_id: ObjectId) -> bool:
        return bool(await users_db.count_documents(
            {'_id': user_id, 'deleted': {'$exists': False}}
        ))

    @staticmethod
    async def is_login_taken(login: str) -> bool:
        login = sha256(login.encode()).hexdigest()
        return bool(await users_db.count_documents(
            {'login': login}
        ))

    @staticmethod
    async def get_salt_by_login(login: str):
        salt = await users_db.find_one(
            {"login": login, 'deleted': {'$ne': True}},
            {"salt": 1}
        )

        return salt['salt']

    @staticmethod
    async def friend_code_owner_id(friend_code: str) -> User._id:
        user_id = (await users_db.find_one(
            {"friend_code": friend_code},
            {"_id": 1, "total": 1}
        )).get('_id')

        if user_id is None:
            raise ValueError("No such friend code")

        return user_id

    @staticmethod
    async def valid_user_id(user_id: ObjectId, bot=False) -> bool:
        user = await users_db.count_documents(
            {
                "$and":
                    [
                        {'_id': user_id}, {'bot': bot},
                        {'deleted': {'$exists': False}}
                    ]
            }
        )
        return bool(user)

    class exc:
        class UserIsNotBot(TypeError):
            pass

        class UserIsBot(TypeError):
            pass

        class UserAlreadyExists(ValueError):
            pass

        class UserNotFound(ValueError):
            pass

        class NotEnoughAuthCredentials(ValueError):
            pass

        class InvalidValueProvided(ValueError):
            pass

        class NoUpdateFieldsProvided(ValueError):
            pass

        class InvalidFriendCode(ValueError):
            pass

        class AlreadyInRelationships(ValueError):
            pass
