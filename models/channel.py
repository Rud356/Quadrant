from enum import IntEnum
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field


class ChannelType:
    dm = 0
    group = 1
    server_text = 2


@dataclass
class DMChannel:
    id: int
    last_message: int = None
    members: List[int] = field(default_factory=list, default=[])
    created_at: datetime


@dataclass
class GroupDMChannel:
    id: int
    name: str
    owner: int
    topic: str = ''
    nsfw: bool = False
    last_message: int = None
    members_limit: int = 25
    members: List[int] = field(default_factory=list, default=[])
    created_at: datetime


@dataclass
class TextChannel:
    id: int
    name: str
    owner: int
    # server that has channel
    parent: int
    last_message: int = None

    nsfw: bool = False
    topic: str = ''

    position: int
    category: int

    permissions: List[bool]
    overwrites: Dict[int, List[bool]] = {}


@dataclass
class CategoryChannel:
    id: int
    name: str
    owner: int
    parent: int
    position: int
    overwriters: Dict[int, List[bool]] = {}


@dataclass
class VoiceChannel:
    id: int
    name: str
    owner: int
    parent: int
    position: int
    categoty: int = None
    bitrate: int = 64*1024