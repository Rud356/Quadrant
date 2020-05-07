from app import client
from typing import List
from datetime import datetime
from dataclasses import dataclass, field

from .enums import ChannelType


db = client.members


@dataclass
class Member:
    _id: int
    color: int = 0xFFFFFF
    endpoint: int
    endpoint_type: int = ChannelType.group
    nickname: str = None
    roles: List[int] = []
