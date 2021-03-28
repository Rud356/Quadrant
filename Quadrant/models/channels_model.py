from __future__ import annotations

from uuid import uuid4, UUID

from sqlalchemy import Column, String, Boolean, ForeignKey, and_
from sqlalchemy.orm import relationship
from sqlalchemy.exc import NoResultFound
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa

from .db_init import Base
from Quadrant import models


class DirectMessagesChannel(Base):
    channel_id = Column(db_UUID, primary_key=True, default=uuid4)

    participants = relationship(models.DMParticipant)
    __tablename__ = "dm_channels"

    async def other_participant(self, requester_user: models.User) -> models.User:
        participant = await self.participants.filter(models.DMParticipant.user_id != requester_user.id).one()
        return participant.user

    @classmethod
    async def create_channel(cls, initiator: models.User, with_user: models.User, *, session):
        new_channel = DirectMessagesChannel(
            participants=[
                models.DMParticipant(user_id=initiator.id),
                models.DMParticipant(user_id=with_user.id)
            ]
        )
        await session.commit()

        return new_channel

    @classmethod
    async def get_channel_by_id(cls, channel_id: UUID, *, session):
        return await session.get(cls, channel_id)

    @classmethod
    async def get_channel_by_participants(cls, requester: models.User, with_user: models.User, *, session):
        return await cls._channel_by_participants(cls, requester, with_user, session=session).one()

    @classmethod
    async def create_or_get_channel_by_participants(cls, requester: models.User, with_user: models.User, *, session):
        try:
            return await cls.get_channel_by_participants(requester, with_user, session=session)

        except NoResultFound:
            # TODO: add check on if user wants to add dms with anyone
            return await cls.create_channel(requester, with_user, session=session)

    @staticmethod
    async def participants_have_channel(
        cls: DirectMessagesChannel, requester: models.User, with_user: models.User, *, session
    ) -> bool:
        return await cls._channel_by_participants(
            cls, requester, with_user, session=session
        ).exists().scalar() or False

    @staticmethod
    def _channel_by_participants(cls, requester: models.User, with_user: models.User, *, session):
        return session.query(cls).filter(
            cls.participants.all_(
                models.DMParticipant.user_id.in_(
                    (requester.id, with_user.id)
                )
            )
        )
