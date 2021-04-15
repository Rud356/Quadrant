from sqlalchemy import Column, ForeignKey

from Quadrant.models import DMParticipant


class GroupParticipant(DMParticipant):
    channel_id = Column(ForeignKey('group_channels.channel_id'))

    __tablename__ = "group_channel_participants"