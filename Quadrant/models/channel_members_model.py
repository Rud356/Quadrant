from __future__ import annotations
from uuid import uuid4, UUID

from sqlalchemy import Column, String, Boolean, ForeignKey, BigInteger, and_
from sqlalchemy.orm import relationship, declared_attr

from .db_init import Base
from Quadrant import models


class DMParticipant(Base):
    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    channel_id = Column(ForeignKey('dm_channels.channel_id'))

    user = relationship("User", lazy='joined', uselist=False)
