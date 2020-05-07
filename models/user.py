from app import client
from typing import List
from random import choices
from datetime import datetime
from dataclasses import dataclass, field

#* my modules


db = client.chat_users


@dataclass
class UserModel:
    _id: int
    token: str = field(repr=False)
    login: str = field(repr=False, default=None)
    password: str = field(repr=False, default=None)
    bot: bool = False
    parent: int = None
    text_status: str = None
    created_at: datetime

    blocked: List[int] = field(default_factory=list, default=[], repr=False)
    friends: List[int] = field(default_factory=list, default=[], repr=False)
    pendings_outgoing: List[int] = field(default_factory=list, default=[], repr=False)
    pendings_incoming: List[int] = field(default_factory=list, default=[], repr=False)

    @staticmethod
    def valid_userID(id, bot=False) -> bool:
        user = db.count_documents( {"$and": [{'_id': id}, {'bot': bot}]} )
        return bool(user)

    @staticmethod
    def available_token(token) -> bool:
        user = db.count_documents( {'token': token} )
        return not bool(user)

    @staticmethod
    def create_token():
        letters_set = '1234567890abcdef'
        token = choices(letters_set, k=256)
        while not UserModel.available_token(token):
            token = choices(letters_set, k=256)

        return token

    @classmethod
    def create_user(
        cls,
        nick: str, bot=False,
        login: str = None,
        password: str = None,
        parent: int = None
        ) -> cls:
        if bot and parent:
            if cls.valid_userID(parent):
                token = cls.create_token()

                user = {
                    'bot': bot,
                    'nick': nick,
                    'parent': parent,
                    'token': token,
                    'created_at': datetime.utcnow()
                }
                db.insert_one(user)

                return cls(**user)

            #? user that trying to create bot
            #? is not valid or bot
            else:
                raise cls.exc.InvalidUser("User doesn't exits")

        #?if our user is regular
        elif login and password:
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
            db.insert_one(user)

            return cls(**user)

        else:
            #? not enough data
            raise ValueError("Not enough data")

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
    def by_id(cls, user_id):
        user = db.find_one({'_id': user_id})

        if not user:
            raise cls.exc.InvalidUser("User id doesn't exists")

        return cls(**user)

    @property
    def is_bot(self) -> bool:
        return self.bot

    @property
    def my_pendings(self):
        return self.pendings_incoming

    @property
    def outgoing_pendings(self):
        return self.pendings_outgoing

    @property
    def my_friends(self):
        return self.friends

    @property
    def blocked(self):
        return self.blocked

    def send_request(self, user_id) -> bool:
        #TODO: get ids using somewhat friend codes
        if not UserModel.valid_userID(user_id) or self.is_bot:
            raise self.exc.InvalidUser("Must be an regular user")

        db.update_one({'_id': self._id}, {'$push': {'pendings_outgoing': user_id}})
        db.update_one({'_id': user_id}, {'$push': {'pendings_incoming': self._id}})
        return True

    def respond_pending(self, user_id, confirm: bool):
        if user_id not in self.my_pendings:
            raise self.exc.UserNotInGroup("User isn't in pendings")

        db.update_one({'_id': user_id}, {'$pull': {'pendings_outgoing': self._id}})
        db.update_one({'_id': self._id}, {'$pull': {'pendings_incoming': user_id}})

        if confirm:
            db.update_one({'_id': self._id}, {'$push': {'friends': user_id}})
            db.update_one({'_id': user_id}, {'$push': {'friends': self._id}})

    def cancel_pending(self, user_id):
        if user_id not in self.outgoing_pendings:
            raise self.exc.UserNotInGroup("User isn't in outgoing pendings")

        db.update_one({'_id': self._id}, {'$pull': {'pendings_outgoing': user_id}})
        db.update_one({'_id': user_id}, {'$pull': {'pendings_incoming': self._id}})

    def delete_friend(self, user_id) -> bool:
        if user_id not in self.my_friends:
            raise self.exc.UserNotInGroup("User isn't in friend list")

        db.update_one({'_id': self._id}, {'$pull': {'friends': user_id}})
        db.update_one({'_id': user_id}, {'$pull': {'friends': self._id}})

    def block_user(self, user_id) -> bool:
        if not self.valid_userID(user_id) or (user_id in self.blocked):
            raise self.exc.InvalidUser("User is already blocked or invalid")

        if user_id in self.outgoing_pendings:
            self.cancel_pending(user_id)

        if user_id in self.pendings_incoming:
            self.respond_pending(user_id, False)

        if user_id in self.my_friends:
            self.delete_friend(user_id)

        db.update_one({'_id': self._id}, {'$push': {'blocked': user_id}})

    def unblock_user(self, user_id) -> bool:
        if user_id not in self.blocked():
            raise self.exc.UserNotInGroup("User isn't blocked")

        db.update_one({'_id': self._id}, {'$pull': {'blocked': user_id}})

    def __repr__(self):
        return super().__repr__()

    class exc:
        class UserNotInGroup(ValueError): ...
        class InvalidUser(ValueError): ...
