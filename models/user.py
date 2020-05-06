from typing import List
from datetime import datetime
from dataclasses import dataclass, field

#* my modules


@dataclass
class UserModel:
    id: int
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
        ...

    @classmethod
    def create_user(
        cls,
        nick: str, bot=False,
        login: str = None,
        password: str = None,
        belongs_to: int = None
        ) -> cls:
        if bot and belongs_to:
            if cls.valid_userID(belongs_to):
                pass

            #? user that trying to create bot
            #? is not valid or bot
            else:
                raise ValueError()

        #?if our user is regular
        elif login and password:
            pass

        else:
            #? not enough data
            raise ValueError()

    @classmethod
    def authorize(cls, login='', password='', token=''):
        if token:
            ...

        elif login and password:
            ...

        else:
            raise cls.exc.InvalidUser('No such user')

    @classmethod
    def by_id(cls, user_id):
        user = session.query(UserModel).select()\
            .filter(UserModel == id)

        if not user:
            raise cls.exc.InvalidUser("User id doesn't exists")

    @property
    def is_bot(self) -> bool:
        return self.bot

    @property
    def my_pendings(self):
        pass

    @property
    def outgoing_pendings(self):
        pass

    @property
    def my_friends(self):
        pass

    @property
    def blocked(self):
        pass

    def send_request(self, user_id) -> bool:
        #TODO: get ids using somewhat friend codes
        if not self.valid_userID(user_id) or self.is_bot:
            raise self.exc.InvalidUser("Must be an regular user")

        pass

    def respond_pending(self, user_id, confirm: bool) -> bool:
        if user_id not in self.my_pendings:
            raise self.exc.UserNotInGroup("User isn't in pendings")

        pass

    def delete_friend(self, user_id, commit=True) -> bool:
        if user_id not in self.my_friends:
            raise self.exc.UserNotInGroup("User isn't in friend list")

        pass

    def block_user(self, user_id) -> bool:
        if not self.valid_userID(user_id) or user_id in self.blocked:
            raise self.exc.InvalidUser("User is already blocked or invalid")

        if user_id in self.my_friends:
            self.delete_friend(user_id, False)

        pass

    def unblock_user(self, user_id) -> bool:
        if user_id not in self.blocked():
            raise self.exc.UserNotInGroup("User isn't blocked")

        pass

    class exc:
        class UserNotInGroup(ValueError): ...
        class InvalidUser(ValueError): ...
