from typing import List

class UserModel:
    def __init__(
        self, id: int, name: str,
        avatar: str=None, bot: bool=False,
        friends: List[UserModel.id]=[],
        blocked: List[UserModel.id]=[],
        pending: List[UserModel]=[]
    ):
        self._id = id
        self._name = name
        self._avatar = avatar
        self._bot = bot
        self._friends = friends
        self._blocked = blocked
        self._pending = pending
        self._ws = None

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property.setter
    def name(self, value: str) -> bool:
        if isinstance(value, str):
            self._name = value
            return True
        else:
            return False

    @property
    def avatar(self) -> str:
        return self._avatar

    @property.setter
    def avatar(self, value: str) -> bool:
        if isinstance(value, str):
            self._avatar = value
            return True
        else:
            return False

    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def friends(self) -> List[UserModel.id]:
        return self._friends

    def accept_pending(self, new_friend: UserModel.id):
        pass

    def add_friend(self, friend_id: UserModel.id) -> bool:
        pass

    def remove_frined(self, friend_id: UserModel.id) -> bool:
        #TODO: finish
        pass

    def block_user(self, blocking_id: UserModel.id) -> bool:
        pass

    def unblock_user(self, blocking_id: UserModel.id) -> bool:
        pass

    @classmethod
    def auth_classic(cls, login: str, password: str) -> cls:
        pass

    @classmethod
    def auth_token(cls, token: str) -> cls:
        pass

    @staticmethod
    def generate_token():
        pass

    def __repr__(self):
        return {
            "id": self.id,
            "name": self.name,
            "avatar": self.avatar,
            "bot": self.bot,
        }

    @classmethod
    def get_by_id(cls, id):
        #TODO: fix code
        return cls.__repr__()