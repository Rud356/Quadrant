from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import declared_attr

from Quadrant.models import users_package
from Quadrant.models.abstract.message import ABCMessage
from .exceptions import BlockedByOtherParticipantException


class DM_Message(ABCMessage):
    __tablename__ = "dm_messages"
    __mapper_args__ = {'polymorphic_identity': 'dm_message', 'concrete': True}

    @declared_attr
    def channel_id(self):
        return Column(ForeignKey("dm_channels.channel_id"), index=True, nullable=False)

    @declared_attr
    def author_id(self):
        return Column(ForeignKey('users.id'), nullable=False)

    async def user_can_send_message_check(self, author: users_package.User, *, session) -> None:
        if users_package.UsersRelations.get_any_relationships_status_with(
            author.id, await self.other_participant(author), session=session
        ) == users_package.UsersRelationType.blocked:
            raise BlockedByOtherParticipantException("User has been blocked by other participant")
