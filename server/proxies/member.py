from typing import List

from proxies.user import UserModel
from proxies.channel import (
    PrivateDM, DM, GroupDM,
    Channel, BaseChannel
)
from proxies.servers import ServerModel
Roles = "placeholder"

class MemberModel:
    def __init__(
        self, id: int, nickname: str=None,
        roles: List[Roles]=[],
        joined_at: int=1,
        deaf: bool = False,
        mute: bool = False,
        member_of: BaseChannel or ServerModel = None
    ):
        self._id = id
        self._nickname = nickname
        self._roles = roles
        self._joined_at = joined_at
        self._deaf = deaf
        self._mute = mute
        self._member_of = member_of

    @property
    def id(self) -> int:
        return self.id

    @property
    def user(self) -> dict:
        # return user object by id
        return UserModel.get_by_id(self._id)

    @property
    def roles(self):
        return self._roles

    @property
    def member_of(self):
        return self._member_of

    def add_role(self, role_id: Roles) -> bool:
        if isinstance(role_id, int):
            #add role
            return True
        else:
            return False

    def remove_role(self, role_id: Roles) -> bool:
        if isinstance(role_id, int) and role_id in self.roles:
            #del role
            return True
        else:
            return False

    def leave(self):
        pass

    def ban(
        self, member: MemberModel, reason: str="Not listed"
    ) -> bool:
        if issubclass(self._member_of, ServerModel):
            # banning person
            return True
        else:
            return False

    def kick(
        self, member: MemberModel, reason: str="Not listed"
    ) -> bool:
        if issubclass(self.member_of, ServerModel):
            # kicking person
            return True
        else:
            return False

    def calculate_permissions(self) -> int:
        if issubclass(self.member_of, ServerModel):
            # calc permissions
            return True
        else:
            return False

    def channel_permissions(self, channel_id: int):
        if issubclass(self.member_of, ServerModel):
            # check deeper and other
            return True
        else:
            return False