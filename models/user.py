from app import client
from typing import List
from bson import ObjectId
from random import choices
from datetime import datetime
from dataclasses import dataclass, field
from pymongo import InsertOne, DeleteMany, ReplaceOne, UpdateOne

db = client.chat_users


@dataclass
class User:
    _id: ObjectId
    token: str = field(repr=False)
    login: str = field(repr=False, default=None)
    password: str = field(repr=False, default=None)
    bot: bool = False
    parent: int = None
    text_status: str = None
    created_at: datetime

    blocked: List[ObjectId] = field(default=[], repr=False)
    friends: List[ObjectId] = field(default=[], repr=False)

    pendings_outgoing: List[ObjectId] = field(default=[], repr=False)
    pendings_incoming: List[ObjectId] = field(default=[], repr=False)

    # creating token
    @staticmethod
    def create_token():
        letters_set = '1234567890abcdef'
        token = choices(letters_set, k=256)
        #TODO: maybe get rid of part below for speed sake

        while not User.available_token(token):
            token = choices(letters_set, k=256)

        return token

    @staticmethod
    def available_token(token) -> bool:
        exists = db.count_documents( {'token': token} )
        return not bool(exists)

    @staticmethod
    def valid_user_id(user_id: ObjectId, bot=False) -> bool:
        user = db.count_documents( {"$and": [{'_id': user_id}, {'bot': bot}]} )
        return bool(user)

    @staticmethod
    def check_blocked(users_block_list: ObjectId, user_checking: ObjectId):
        is_blocked = db.count_documents(
            {"$and": [{"_id": users_block_list}, {"blocked": {"$in": [user_checking]}}]}
        )
        return bool(is_blocked)

    @classmethod
    def authorize(cls, login='', password='', token=''):
        if token:
            user = db.find_one({'token': token})
            if user is None:
                raise ValueError('No such token')

            return cls(**user)

        elif login and password:
            user = db.find_one({'login': login, 'password': password})
            if user is None:
                raise ValueError('No such user')

            return cls(**user)

        else:
            raise cls.exc.InvalidUser('No such user')

    @classmethod
    def from_id(cls, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        user = db.find_one({'_id': user_id})

        if not user:
            raise cls.exc.InvalidUser("User id doesn't exists")

        return cls(**user)

    @classmethod
    def create_user(
        cls, nick: str, bot=False, login: str = None, password: str = None,
        parent: str = None
        ):
        if bot and parent:
            # likely raises bson.errors.InvalidId
            parent = ObjectId(parent)
            if cls.valid_user_id(parent):
                token = cls.create_token()

                user = {
                    'bot': bot,
                    'nick': nick,
                    'token': token,
                    'parent': parent,
                    'created_at': datetime.utcnow()
                }
                id = db.insert_one(user).inserted_id

                return cls(_id=id, **user)

            else:
                raise cls.exc.InvalidUser("User doesn't exits")

        elif login and password:
            if db.find_one({'login': login, 'password': password}):
                raise ValueError("Disallowed")

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
            id = db.insert_one(user).inserted_id

            return cls(_id=id, **user)

        else:
            #? not enough data
            raise ValueError("Not enough data")

    def send_friend_request(self, user_id: str) -> bool:
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        if (
            (
                self.valid_user_id(user_id) and
                self.check_blocked(self._id, user_id)
            ) and

            not self.bot and

            (
                user_id not in self.blocked and
                user_id not in self.pendings_incoming and
                user_id not in self.pendings_outgoing and
                user_id not in self.friends
            )
        ):
            db.bulk_write([
                UpdateOne({"_id": self._id}, {"$push": {"pendings_outgoing": user_id}}),
                UpdateOne({"_id": user_id}, {"$push": {"pendings_incoming": self._id}})
            ])

        raise self.exc.InvalidUser("You can't sent friend request to this user")

    def cancel_friend_request(self, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        if user_id not in self.pendings_outgoing:
            raise self.exc.UserNotInGroup("User isn't in outgoing pendings")

        db.bulk_write([
                UpdateOne({"_id": self._id}, {"$pull": {"pendings_outgoing": user_id}}),
                UpdateOne({"_id": user_id}, {"$pull": {"pendings_incoming": self._id}})
            ])

    def responce_friend_request(self, user_id: str, confirm=True):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
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

        db.bulk_write(operations)

    def delete_friend(self, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        if user_id not in self.friends:
            raise self.exc.UserNotInGroup("User isn't in friend list")

        db.bulk_write([
            UpdateOne({'_id': self._id}, {'$pull': {'friends': user_id}}),
            UpdateOne({'_id': user_id}, {'$pull': {'friends': self._id}})
        ])

    def block_user(self, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)
        if not self.valid_user_id(user_id) or (user_id in self.blocked):
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

        db.bulk_write(operations)

    def unblock_user(self, user_id: str):
        # likely raises bson.errors.InvalidId
        user_id = ObjectId(user_id)

        if user_id not in self.blocked:
            raise self.exc.UserNotInGroup("User isn't blocked")

        db.update_one({'_id': self._id}, {'$pull': {'blocked': user_id}})

    class exc:
        class UserNotInGroup(ValueError): ...
        class InvalidUser(ValueError): ...
