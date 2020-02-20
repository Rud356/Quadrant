from typing import List, Mapping

from proxies.user import UserModel
from proxies.member import MemberModel
from proxies.channel_types import ChannelTypes

class BaseChannel:
    def __init__(
        self, id: int, ch_type: int,
        name: str, last_msg_id: int,
        recievers:List[MemberModel] = []
    ):
        self._id = id
        self._ch_type = ch_type
        self._name = name
        self._last_msg_id = last_msg_id
        self._recievers = recievers

    @property
    def id(self):
        return self._id

    @property
    def ch_type(self):
        return self._ch_type

    @property
    def name(self):
        return self._name

    @property
    def last_msg_id(self):
        return self._last_msg_id

    @property.setter
    def last_msg_id(self, msg_id: int):
        pass

    @property
    def recievers(self):
        return self._recievers

    async def send_message(self, msg):
        pass

    async def join_channel(self, user: UserModel):
        pass

    def __repr__(self):
        return {
            "id": self.id,
            "ch_type": self.ch_type,
            "name": self.name,
            "last_msg_id": self.last_msg_id,
            "recievers": self.recievers
        }

class PrivateDM(BaseChannel):
    def __init__(
        self, id: int, ch_type: int=ChannelTypes.pdm,
        name: str="Undefined", last_msg_id: int=0,
        recievers:Mapping[MemberModel, MemberModel]=[]
    ):
        BaseChannel.__init__(
            self, id, ch_type, name,
            last_msg_id, recievers
        )

    def join_channel(self, user):
        raise NotImplementedError("This method cant be used in pm")

    def exchange_keys_mechanism(self):
        pass

class DM(BaseChannel):
    def __init__(
        self, id: int, ch_type: int=ChannelTypes.dm,
        name: str="Undefined", last_msg_id: int=0,
        recievers:Mapping[MemberModel, MemberModel]=[]
    ):
        BaseChannel.__init__(
            self, id, ch_type, name,
            last_msg_id, recievers
        )

    def join_channel(self, user):
        raise NotImplementedError("This method cant be used in pm")

class GroupDM(BaseChannel):
    def __init__(
        self, id: int, ch_type: int=ChannelTypes.group_dm,
        name: str="Undefined", last_msg_id: int=0,
        recievers: List[MemberModel]=[]
    ):
        BaseChannel.__init__(
            self, id, ch_type, name,
            last_msg_id, recievers
        )

    async def join_channel(self, user):
        if len(self._recievers) <= 10:
            return await super().join_channel(user)
        else:
            pass

class Channel(BaseChannel):
    def __init__(
        self, id: int, ch_type: int=ChannelTypes.channel,
        name: str="Undefined", last_msg_id: int=0,
        recievers: List[MemberModel]=[],
        parent_id: int = 0,
        overwrites = []
    ):
        BaseChannel.__init__(
            self, id, ch_type, name,
            last_msg_id, recievers
        )
        self._parent_id = parent_id
        self._overwrites = overwrites

    @property
    def parent_id(self):
        return self._parent_id

    @property
    def overwrites(self):
        return self._overwrites

    def __repr__(self):
        base = super().__repr__()
        base["parent_id"] = self.parent_id
        base["overwrites"] = self.overwrites