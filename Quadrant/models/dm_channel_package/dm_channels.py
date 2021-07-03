from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, declared_attr, relationship

from Quadrant.models import users_package
from Quadrant.models.db_init import AsyncSession, Base
from Quadrant.quadrant_logging import gen_log
from .channel_members import DMParticipant
from .dm_messages import DM_Message


class DirectMessagesChannel(Base):
    channel_id: Mapped[UUID] = Column(db_UUID(as_uuid=True), primary_key=True, default=uuid4)

    participants: Mapped[List[DMParticipant]] = relationship(
        DMParticipant, lazy='joined', cascade="all, delete-orphan"
    )
    __tablename__ = "dm_channels"

    @declared_attr
    def _messages(cls) -> Optional[Mapped[DM_Message]]:
        _messages = relationship(
            DM_Message, lazy="noload", cascade="all, delete-orphan",
            primaryjoin=lambda: DM_Message.channel_id == DirectMessagesChannel.channel_id
        )

    async def other_participant(self, requester_user: users_package.User) -> DMParticipant:
        """
        Gives other participant instance.

        :param requester_user: participant that asks for instance of other participant.
        :return: DMParticipant instance.
        """
        # TODO: check if it'll be faster to iterate through list of participants
        participant = await self.participants.filter(DMParticipant.user_id != requester_user.id).one()
        return participant

    @classmethod
    async def create_channel(
        cls, initiator: users_package.User, with_user: users_package.User,
        *, session: AsyncSession
    ):
        """
        Initializes new dm channel.

        :param initiator: participant who initiates dm channel.
        :param with_user: participant instance with whom we create dm channel.
        :param session: sqlalchemy session.
        :return: new dm channel instance.
        """
        # TODO: add setting to limit initiation of dms channels per server or based on something else.

        new_channel = DirectMessagesChannel(
            participants=[
                DMParticipant(user_id=initiator.id),
                DMParticipant(user_id=with_user.id)
            ]
        )
        await session.commit()

        return new_channel

    @classmethod
    async def get_channel_by_id(
        cls, channel_id: UUID, requester: users_package.User,
        *, session: AsyncSession
    ):
        """
        Gives exact dm channel
        :param channel_id: channel id.
        :param requester: participant instance of someone who asks for channel.
        :param session: sqlalchemy session.
        :return:
        """
        try:
            return await session.filter(
                cls.participants.id.is_(requester.id)
            ).get(cls, channel_id)

        except (NoResultFound, OverflowError):
            gen_log.debug(f"Private channel with id {channel_id} not found for user with id {requester.id}")
            raise ValueError("No such dm channel with specified id")

    @classmethod
    async def get_channel_by_participants(
        cls, requester: users_package.User, with_user: users_package.User,
        *, session: AsyncSession
    ):
        """
        Returns a channel object, selected by two members of channel.
        :param requester: user, who requested channel.
        :param with_user: user with whom we look channel for.
        :param session: sqlalchemy session.
        :return: dm channel object.
        """
        query_result = await session.execute(cls._channel_by_participants_query(cls, requester, with_user))

        try:
            channel = await query_result.scalar_one()

        except NoResultFound:
            gen_log.debug(f"Channel with participants {requester.id} and {with_user.id} not found")
            raise

        return channel

    @classmethod
    async def get_or_create_channel_by_participants(
        cls, requester: users_package.User, with_user: users_package.User,
        *, session: AsyncSession
    ):
        """
        Gets channel by participants and in case it wasn't found - creates new one.

        :param requester: participant instance of someone who asks for channel.
        :param with_user: participant instance with whom we want to get channel in too.
        :param session: sqlalchemy session.
        :return: dm channel.
        """
        try:
            return await cls.get_channel_by_participants(requester, with_user, session=session)

        except NoResultFound:
            # TODO: add check on if participant wants to add dms with anyone
            return await cls.create_channel(requester, with_user, session=session)

    @staticmethod
    async def participants_have_channel(
        cls: DirectMessagesChannel, requester: users_package.User,
        with_user: users_package.User, *, session: AsyncSession
    ) -> bool:
        """
        Checks if participants have channel.

        :param cls: DirectMessagesChannel class.
        :param requester: participant instance of someone who asks for channel.
        :param with_user: participant instance with whom we want to get channel in too.
        :param session: sqlalchemy session.
        :return: dm channel.
        """
        query = cls._channel_by_participants_query(
            cls, requester, with_user
        ).exists()
        query_result = await session.execute(query) # noqa: exists() is valid method for expressions

        return query_result.scalar() or False

    @staticmethod
    def _channel_by_participants_query(cls, requester: users_package.User, with_user: users_package.User):
        """
        Gives query that helps finding channels where both participants are in.

        :param cls: DirectMessagesChannel class.
        :param requester: participant instance of someone who asks for channel.
        :param with_user: participant instance with whom we want to get channel in too.
        :return: sqlalchemy query.
        """
        return select(cls).filter(
            cls.participants.all_(
                DMParticipant.user_id.in_((requester.id, with_user.id))
            )
        )

    @staticmethod
    async def is_member(channel_id: UUID, user: users_package.User, *, session) -> bool:
        """
        Checks if participant is member of this channel.

        :param channel_id: channel id.
        :param user: participant instance of someone who asks for channel.
        :param session: sqlalchemy session.
        :return: bool value representing if participant is a member.
        """
        exists_query = select(DMParticipant).filter(
            DMParticipant.user_id == user.id,
            DMParticipant.channel_id == channel_id
        ).exists()
        exists_query_result = await session.execute(exists_query)

        return (await exists_query_result.scalar()) or False
