from __future__ import annotations

from typing import TYPE_CHECKING

from uuid import UUID
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, relationship

from Quadrant.models import users_package
from Quadrant.models.db_init import AsyncSession
from Quadrant.models.abstract.message import ABCMessage
from .exceptions import BlockedByOtherParticipantException

if TYPE_CHECKING:
    from .channel_members import DMParticipant
    from .dm_channels import DirectMessagesChannel


class DM_Message(ABCMessage):
    __tablename__ = "dm_messages"
    __mapper_args__ = {'polymorphic_identity': 'dm_message', 'concrete': True}

    channel: DirectMessagesChannel

    @declared_attr
    def channel_id(self) -> Mapped[UUID]:
        return Column(ForeignKey("dm_channels.channel_id"), index=True, nullable=False)

    @declared_attr
    def channel(self) -> DirectMessagesChannel:
        return relationship("DirectMessagesChannel", lazy="joined", uselist=False)  # noqa: this is other way
        # to declare relationships

    async def can_user_send_message_check(
        self, author: users_package.User, *, session: AsyncSession
    ) -> None:
        other_participant: DMParticipant = self.channel.other_participant(author)

        if users_package.UserRelation.is_in_blocked_relations(
            author.id, other_participant.id,
            session=session
        ):
            raise BlockedByOtherParticipantException("User has been blocked by other participant")
