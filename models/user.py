from random import choices
from datetime import datetime

from typing import List
from bson import ObjectId
from dataclasses import dataclass, field

# my modules
from app import db
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne

from .endpoint import MetaEndpoint, DMchannel

users_db: AsyncIOMotorCollection = db['chat_users']


@dataclass
class User:
    _id: ObjectId
    created_at: datetime
    nick: str

    bot: bool = False
    token: str = None
    code: str = field(repr=False, default=None)
    parent: int = None
    text_status: str = None


    blocked: List[ObjectId] = field(default_factory=list, repr=False)
    friends: List[ObjectId] = field(default_factory=list, repr=False)

    pendings_outgoing: List[ObjectId] = field(default_factory=list, repr=False)
    pendings_incoming: List[ObjectId] = field(default_factory=list, repr=False)


    @staticmethod
    def create_token():
        letters_set = '1234567890abcdef'
        token = ''.join(choices(letters_set, k=64))
        return token

    @staticmethod
    async def valid_user_id(user_id: ObjectId, bot=False) -> bool:
        user = await users_db.count_documents( {"$and": [{'_id': user_id}, {'bot': bot}]} )
        return bool(user)

    @staticmethod
    async def check_blocked(users_block_list: ObjectId, user_checking: ObjectId):
        is_blocked = await users_db.count_documents(
            {"$and": [{"_id": users_block_list}, {"blocked": {"$in": [user_checking]}}]}
        )
        return bool(is_blocked)

    @staticmethod
    async def avaliable_friend_code(code: str):
        same_codes = await users_db.count_documents(
            {"code": code}
        )
        return not bool(same_codes)

    @staticmethod
    async def friendcodes_owner(code: str) -> ObjectId:
        user_id = await users_db.find_one({"code": code}, {"_id": 1, "total": 1})
        return user_id.get('_id')

    @classmethod
    async def from_id(cls, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        user = await users_db.find_one(
            {'_id': user_id},
            {
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
        )

        if not user:
            raise cls.exc.InvalidUser("User id doesn't exists")

        return cls(**user)

    @classmethod
    async def authorize(cls, login='', password='', token=''):
        if token:
            user = await users_db.find_one(
                {'token': token},
                {
                    "login": 0,
                    "password": 0,
                }
            )

            if user is None:
                raise ValueError('No such token')

            return cls(**user)

        elif login and password:
            user = await users_db.find_one(
                {'login': login, 'password': password},
                {
                    "login": 0,
                    "password": 0,
                }
            )
            if user is None:
                raise ValueError('No such user')

            return cls(**user)

        else:
            raise cls.exc.InvalidUser('No such user')

    @classmethod
    async def create_user(
        cls,
        nick: str, bot=False,
        login: str = '', password: str = '',
        parent: ObjectId = None, **_
        ):
        if bot and parent:
            if cls.valid_user_id(parent):
                token = cls.create_token()

                user = {
                    'bot': bot,
                    'nick': nick,
                    'token': token,
                    'parent': parent,
                    'created_at': datetime.utcnow()
                }
                id = await users_db.insert_one(user)
                user['_id'] = id.inserted_id
                return cls(**user)

            else:
                raise cls.exc.InvalidUser("User doesn't exits")

        elif login and password:
            #TODO: idk how to make sure that this is unique info faster
            if await users_db.find_one({'login': login}):
                raise ValueError("Disallowed registration")

            if len(login) < 5 or len(password) < 10:
                raise ValueError("Too short password or login")

            token = cls.create_token()

            user = {
                'bot': False,
                'nick': nick,
                'login': login,
                'password': password,
                'token': token,
                'blocked': [],
                'friends': [],
                'pendings_outgoing': [],
                'pendings_incoming': [],
                'created_at': datetime.utcnow()
            }
            id = await users_db.insert_one(user)
            user['_id'] = id.inserted_id
            return cls(**user)

        else:
            #? not enough data
            raise ValueError("Not enough data")

    async def send_friend_request(self, user_id: ObjectId) -> bool:
        if (
            (
                await self.valid_user_id(user_id) and not
                await self.check_blocked(self._id, user_id)
            ) and

                not self.bot and

            (
                user_id not in self.blocked and
                user_id not in self.pendings_incoming and
                user_id not in self.pendings_outgoing and
                user_id not in self.friends
            )
        ):
            await users_db.bulk_write([
                UpdateOne({"_id": self._id}, {"$push": {"pendings_outgoing": user_id}}),
                UpdateOne({"_id": user_id}, {"$push": {"pendings_incoming": self._id}})
            ])

        raise self.exc.InvalidUser("You can't sent friend request to this user")

    async def cancel_friend_request(self, user_id: ObjectId):
        if user_id not in self.pendings_outgoing:
            raise self.exc.UserNotInGroup("User isn't in outgoing pendings")

        await users_db.bulk_write([
                UpdateOne({"_id": self._id}, {"$pull": {"pendings_outgoing": user_id}}),
                UpdateOne({"_id": user_id}, {"$pull": {"pendings_incoming": self._id}})
            ])

    async def responce_friend_request(self, user_id: ObjectId, confirm=True):
        if user_id not in self.pendings_incoming:
            raise self.exc.UserNotInGroup("User isn't in incoming pendings")

        operations = [
            UpdateOne({'_id': user_id}, {'$pull': {'pendings_outgoing': self._id}}),
            UpdateOne({'_id': self._id}, {'$pull': {'pendings_incoming': user_id}})
        ]

        if confirm:
            operations += [
                UpdateOne({'_id': self._id}, {'$push': {'friends': user_id}}),
                UpdateOne({'_id': user_id}, {'$push': {'friends': self._id}})
            ]

        await users_db.bulk_write(operations)

    async def delete_friend(self, user_id: ObjectId):
        if user_id not in self.friends:
            raise self.exc.UserNotInGroup("User isn't in friend list")

        await users_db.bulk_write([
            UpdateOne({'_id': self._id}, {'$pull': {'friends': user_id}}),
            UpdateOne({'_id': user_id}, {'$pull': {'friends': self._id}})
        ])

    async def block_user(self, user_id: ObjectId):
        if not await self.valid_user_id(user_id) or (user_id in self.blocked):
            raise self.exc.InvalidUser("User is already blocked or invalid")

        operations = [
            UpdateOne({'_id': self._id}, {'$push': {'blocked': user_id}})
        ]

        if user_id in self.pendings_incoming:
            operations += [
                UpdateOne({"_id": self._id}, {"$pull": {"pendings_outgoing": user_id}}),
                UpdateOne({"_id": user_id}, {"$pull": {"pendings_incoming": self._id}})
            ]

        if user_id in self.pendings_outgoing:
            operations += [
                UpdateOne({'_id': user_id}, {'$pull': {'pendings_outgoing': self._id}}),
                UpdateOne({'_id': self._id}, {'$pull': {'pendings_incoming': user_id}})
            ]

        if user_id in self.friends:
            operations += [
                UpdateOne({'_id': self._id}, {'$pull': {'friends': user_id}}),
                UpdateOne({'_id': user_id}, {'$pull': {'friends': self._id}})
            ]

        await users_db.bulk_write(operations)

    async def unblock_user(self, user_id: ObjectId):
        if user_id not in self.blocked:
            raise self.exc.UserNotInGroup("User isn't blocked")

        await users_db.update_one({'_id': self._id}, {'$pull': {'blocked': user_id}})

    # For now those are only dms
    async def small_endpoints(self) -> List[DMchannel]:
        """
        Retruns channels like dms and group dms
        """
        endpoints = await MetaEndpoint.get_small_endpoints_from_id(self._id)

        return endpoints

    async def small_endpoint(self, endpoint_id: ObjectId):
        """
        Returns one small endpoint with given id
        """
        endpoint = await MetaEndpoint.get_small_endpoint(self._id, endpoint_id)
        if not endpoint:
            raise ValueError("User isn't a part of endpoint")

        return endpoint

    async def set_nickname(self, new_nickname: str):
        if len(new_nickname) > 50:
            raise ValueError("Too long nickname")

        await users_db.update_one({"_id": self._id}, {"$set": {"nick": new_nickname}})
        self.nick = new_nickname

    async def set_text_status(self, new_status: str):
        if len(new_status) > 256:
            raise ValueError("Too long status")

        await users_db.update_one({"_id": self._id}, {"$set": {"text_status": new_status}})
        self.text_status = new_status

    async def set_friend_code(self, new_code):
        if len(new_code) in range(3, 51):
            raise ValueError("Too long friend code")

        is_avaliable = await self.avaliable_friend_code(new_code)
        if not is_avaliable:
            raise ValueError("Code is already used")

        await users_db.update_one({"_id": self._id}, {"$set": {"code": new_code}})
        self.code = new_code

    class exc:
        class UserNotInGroup(ValueError): ...
        class InvalidUser(ValueError): ...
