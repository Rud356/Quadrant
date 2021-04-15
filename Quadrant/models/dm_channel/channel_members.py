from __future__ import annotations

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from Quadrant import models
from Quadrant.models.db_init import Base


class DMParticipant(Base):
    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    channel_id = Column(ForeignKey('dm_channels.channel_id'))

    user: models.User = relationship("User", lazy='joined', uselist=False)

    __tablename__ = "dm_channel_participants"
