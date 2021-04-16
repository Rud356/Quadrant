from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint

from Quadrant.models.dm_channel_package import DMParticipant


class GroupParticipant(DMParticipant):
    channel_id = Column(ForeignKey('group_channels.channel_id'))

    __table_args__ = (
        PrimaryKeyConstraint("channel_id", "user_id", name="_unique_dm_channel_member"),
    )
    __tablename__ = "group_channel_participants"
