from app import client
from typing import List, Dict
from datetime import datetime
from .enums import ChannelType
from dataclasses import dataclass, field


db = client.channels


@dataclass
class DMChannel:
    _id: int
    last_message: int = None
    members: List[int] = field(default_factory=list, default=[])
    created_at: datetime


@dataclass
class GroupDMChannel:
    _id: int
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
    _id: int
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
    overwrites: Dict[int, Dict[str, bool]] = {}


@dataclass
class CategoryChannel:
    _id: int
    name: str
    owner: int
    parent: int
    position: int
    overwriters: Dict[int, Dict[str, bool]] = {}


@dataclass
class VoiceChannel:
    id: int
    name: str
    owner: int
    parent: int
    position: int
    categoty: int = None
    overwriters: Dict[int, Dict[str, bool]] = {}
    bitrate: int = 64*1024