from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from Quadrant.models import Base
from Quadrant.models.users_package import User


class GroupParticipant(Base):
    user_id = Column(ForeignKey('users.id'), nullable=False)
    channel_id = Column(ForeignKey('group_channels.channel_id'), index=True)

    user: User = relationship("User", lazy='joined', uselist=False)
    __table_args__ = (
        PrimaryKeyConstraint("channel_id", "user_id", name="_dm_channel_member"),
        UniqueConstraint("channel_id", "user_id", name="_unique_dm_channel_member")
    )
    __tablename__ = "group_channel_participants"
