from typing import List

from proxies.channel import Channel
from proxies.member import MemberModel

class ServerModel:
    def __init__(
        self, id: int, name: str,
        icon: str, owner: MemberModel.id,
        default_permissions: int, roles=[],
        emojis=[], created_at: int=0, member_count=1,
        channels: List[Channel]=[]
    ):
        self._id = id
        self._name = name
        self._icon = icon
        self._owner = owner
        self._default_permissions = default_permissions
        self._roles = roles
        self._emojis = emojis
        self._created_at = created_at
        self._member_count = member_count
        self._channels = channels