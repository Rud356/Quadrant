from enum import Enum

class Statuses(Enum):
    offline = 0
    online = 1
    away = 2
    asleep = 3
    dnd = 4

class User:
    def __init__(
        self, id: int, nick: str, bot: bool,
        token: str = None, avatar: str = None,
        friendlist: list = [], blacklist: list = [],
        status = 0
    ):
        self.__id = id
        self.__bot = bot
        self.__nick = nick
        self.__token = token
        self.__avatar = avatar
        self.__friendlist = friendlist
        self.__blacklist = blacklist
        self.__status = status

    @property
    def id(self):
        return self.__id

    @property.deleter
    def id(self):
        #TODO: destroy user
        pass

    @property
    def bot(self):
        return self.__bot

    @property
    def nick(self):
        return self.__nick

    @property.setter
    def nick(self, value):
        pass

    @property
    def avatar(self):
        return self.avatar

    @property.setter
    def avatar(self, value):
        pass

    @property
    def status(self):
        return self.status

    @property.setter
    def status(self, value: int):
        pass

    @property
    def _token(self):
        return self.__token

    @property
    def friendlist(self):
        return self.friendlist

    def append_friend(self, friend: int):
        pass

    def delete_friend(self, unfriended: int):
        pass

    @property
    def blacklist(self):
        return self.blacklist

    def add_blacklist(self, enemy: int):
        pass

    def delete_blacklisted(self, not_enemy: int):
        pass

    def __eq__(self, value):
        if type(value) == User:
            return False
        else:
            return User.__token() == self._token()

    def __ne__(self, value):
        if type(value) != User:
            return True
        else:
            return User.__token() != self._token()

    def to_dict(self):
        return {
            "id": self.id,
            "nick": self.nick,
            "status": self.status,
            "bot": self.bot,
            "avatar": self.avatar,
            "friendlist": self.friendlist,
            "blacklist": self.blacklist
        }

    def __repr__(self):
        return {
            "id": self.id,
            "nick": self.nick,
            "status": self.status,
            "bot": self.bot,
            "avatar": self.avatar,
        }