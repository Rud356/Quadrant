from enum import Enum
from app import db, session
from sqlalchemy import (
    Column,
    BigInteger, Text, VARCHAR,
    Boolean, DateTime, Integer,
    and_
)
from sqlalchemy.orm import Load, load_only, relationship


class ChannelType(Enum):
    dm = 0
    group = 1
    text_channel = 2
    category_channel = 3
    voice_channel = 4



class ChannelModel(db.Model):
    id: int = Column(BigInteger, primary_key=True)
    name: str = Column(VARCHAR(50), default=None, nullable=True)
    members = None #FK
    invites = None #FK
    members_count: int = Column(Integer, default=0)
    channel_type = Column(Enum(ChannelType))
    