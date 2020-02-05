from abc import *
from enum import Enum


class ChatType(Enum):
    private_dm = 0
    dm = 1
    group_dm = 2
    server_channel = 3
    category_channel = 4
    voice_channel = 5


class User(ABC):
    __slots__ = (
        'id', '__username', 'discriminator',
        '__avatar', 'bot', '__token', 'status'
    )

    def __init__(
        self, id: int, username: str, discriminator: int,
        avatar=None, bot=False, token=None, registrated=0
        ):
        self.id = id
        self.discriminator = discriminator
        self.bot = bot
        self.status = status
        self.__avatar = avatar
        self.__username = username
        self.__token = token

    @abstractclassmethod
    def get_user(cls, id):
        pass

    @abstractclassmethod
    def auth_user(cls, **kwargs):
        pass

    @abstractclassmethod
    def create_user(cls, **kwargs):
        pass

    @property
    def avatar(self):
        return self.__avatar

    @abstractproperty
    @avatar.setter
    def avatar(self, value):
        pass

    @abstractproperty
    @avatar.deleter
    def avatar(self):
        pass

    @property
    def username(self):
        return self.__username

    @abstractproperty
    @username.setter
    def username(self, value):
        pass

    def auth_checker(self, token):
        return self.__token == token

    @abstractmethod
    def friends_list(self):
        pass

    @abstractmethod
    def add_friend(self, pending):
        pass

    @abstractmethod
    def del_friend(self, deleting):
        pass

    @abstractmethod
    def blocked_list(self):
        pass

    @abstractmethod
    def blocked_add(self):
        pass

    @abstractmethod
    def blocked_del(self):
        pass

    @abstractmethod
    def __del__(self):
        pass


class RolesPermission(Enum):
    owner = 1 << 31
    admin = 1 << 30
    manage_server = 1 << 29
    manage_channels = 1 << 28
    ban_users = 1 << 27
    kick_users = 1 << 26
    deaf_users = 1 << 25
    mute_users = 1 << 24
    manage_nicknames = 1 << 23
    manage_roles = 1 << 22
    manage_messages = 1 << 13
    view_log = 1 << 21
    view_channel = 1 << 20
    read_messages = 1 << 20
    send_messages = 1 << 19
    change_nicknames = 1 << 18
    create_invites = 1 << 17
    connect = 1 << 16
    speak = 1 << 15
    mention_everyone = 1 << 14


class Roles(ABC):
    __slots__ = (
        'id', '__Name', '__ServerID', '__Permissions', '__Color'
    )
    def __init__(self, id, Name, ServerID, Permissions, Color):
        self.id = id
        self.__Name = Name
        self.__ServerID = ServerID
        self.__Permissions = Permissions
        self.__Color = int(Color, 16)

    def has_permission(self, permission):
        return bool(self.__Permissions & permission)

    @property
    def name(self):
        return self.__Name

    @abstractproperty
    @property.setter
    def name(self, value):
        pass

    @abstractclassmethod
    def create_role(self, **k):
        pass

    @property
    def server_id(self):
        return self.server_id

    @property
    def color(self):
        return self.__Color


class Member(ABC):
    __slots__ = (
        "Origin_user", "__Nick", "__Roles",
        "__Joined_at", "__Deaf", "__Mute", "__Member_of"
    )

    def __init__(
        self, id, nick, roles, joined_at, Member_of, deaf=False, mute=False
        ):
        self.Origin_user = id
        #just temporal, will overwrite with getting user by id
        self.__Nick: str = nick
        self.__Roles: list = roles
        self.__Joined_at = joined_at
        self.__Deaf = deaf, self.__Mute = mute
        self.__Member_of = Member_of

    @abstractclassmethod
    @classmethod
    def join_chat(cls, **k):
        pass

    @abstractmethod
    def leave_chat(self):
        pass

    @abstractmethod
    def kick_member(self):
        pass

    @abstractmethod
    def ban_member(self):
        pass

    @property
    def Nick(self):
        #TODO: add getting nick from origin, if it doesnt exists
        return self.__Nick

    @abstractproperty
    @property.setter
    def Nick(self, value):
        pass

    @property
    def joined_at(self):
        return self.__Joined_at

    @property
    def isDeaf(self):
        return self.__Deaf

    @abstractmethod
    def set_Deaf(self, requester):
        pass

    @property
    def isMute(self):
        return self.__Mute

    @abstractclassmethod
    def set_Mute(self, requester):
        pass

    @abstractmethod
    def calculate_permissions(self):
        pass


class ChatFactory(ABC):
    @abstractstaticmethod
    @staticmethod
    def create_chat(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_dm(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_pdm(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_group_dm(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_server(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_channel(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_voice(**k):
        pass

    @abstractstaticmethod
    @staticmethod
    def create_invite(**k):
        pass


class Channel(ABC):
    __slots__ = (
        "id", "channel_type", "server_id",
        "position", "overwrites", "name", "topic",
        "nsfw", "icon", "owner", "last_message"
    )

    def __init__(self, **kwargs):
        pass

    @property
    def NSFW(self):
        return self.nsfw

    @abstractproperty
    @property.setter
    def NSFW(self, value):
        pass

    #im too lazy to finish this crap so i just make a final views