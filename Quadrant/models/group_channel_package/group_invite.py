from __future__ import annotations

from datetime import datetime, timedelta
from math import ceil
from secrets import token_urlsafe
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, not_, or_, select, ForeignKeyConstraint

from Quadrant.models.db_init import Base
from .group_participant import GroupParticipant

GROUP_INVITES_LIMIT = 25
INVITE_CODE_BIT_LENGTH = 12
# Because token_urlsafe encodes bytes using base64, which splits bits sequence per 6 bits and encodes it as 8 bit chars,
# this is why we must take 8/6 ratio
invite_code_len = ceil(INVITE_CODE_BIT_LENGTH * (8 / 6))


class InvitesExceptions:
    class TooManyInvites(ValueError):
        ...

    class TooShortLifespan(ValueError):
        """Invite must live at least five minutes"""
        ...

    class InvalidUsersLimitValue(ValueError):
        ...


class GroupInvite(Base):
    invite_code = Column(
        String(length=invite_code_len),
        default=lambda: token_urlsafe(INVITE_CODE_BIT_LENGTH), primary_key=True
    )
    group_channel_id = Column(ForeignKey('group_channels.channel_id'), index=True, nullable=False)
    created_by_participant_id = Column(ForeignKey("users.id"))

    expires_at = Column(DateTime(), default=lambda: datetime.utcnow() + timedelta(days=1))
    users_limit = Column(Integer(), default=10)
    users_used_invite = Column(Integer(), default=0)

    __tablename__ = "group_invites"
    __table_args__ = (
        ForeignKeyConstraint(
            (group_channel_id, created_by_participant_id),
            (GroupParticipant.channel_id, GroupParticipant.user_id), name="fk_participants"
        ),
    )

    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at or self.users_used_invite > self.users_used_invite

    @staticmethod
    def get_alive_invites_query():
        """
        Generates basic query to fetch not expired invites from database.

        :return: query.
        """
        cls = GroupInvite
        return select(cls).filter(
            not_(
                or_(
                    datetime.utcnow(), cls.expires_at,
                    cls.users_used_invite > cls.users_used_invite
                )
            )
        )

    @staticmethod
    def get_alive_invites_query_for_channel(group_channel_id: UUID):
        """
        Generates basic query to fetch alive invites from database for specific channel.

        :param group_channel_id: group channel id that we're querying.
        :return: query.
        """
        cls = GroupInvite
        return cls.get_alive_invites_query().filter(
            cls.group_channel_id == group_channel_id
        )

    @staticmethod
    async def get_alive_invites_count(group_channel_id: UUID, *, session) -> int:
        """
        Gives number of alive invites for specific group.

        :param group_channel_id: group channel id that we're querying.
        :param session: sqlalchemy session.
        :return: number of alive invites.
        """
        cls = GroupInvite
        query = select(cls.invite_code).filter(
            not_(
                or_(
                    datetime.utcnow(), cls.expires_at,
                    cls.users_used_invite > cls.users_used_invite
                )
            ), cls.group_channel_id == group_channel_id
        ).count()
        query_result = await session.execute(query)

        return (await query_result.scalar_one_or_none()) or 0

    @classmethod
    async def get_alive_invites(cls, group_channel_id: UUID, *, session) -> GroupInvite:
        query = cls.get_alive_invites_query_for_channel(group_channel_id)
        query_result = await session.execute(query)

        return query_result.all()

    @classmethod
    async def get_invite_by_code(cls, invite_code: str, *, session) -> GroupInvite:
        query = cls.get_alive_invites_query().filter(cls.invite_code == invite_code)
        query_result = await session.execute(query)

        return query_result.scalar_one()

    @classmethod
    async def new_invite(
        cls, created_by_participant_id, group_channel_id: UUID,
        expires_at: Optional[datetime] = None, users_limit: Optional[int] = 10, *, session
    ) -> GroupInvite:
        if (await cls.get_alive_invites_count(group_channel_id, session=session)) > GROUP_INVITES_LIMIT:
            raise InvitesExceptions.TooManyInvites("Too many invites for dm group")

        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(days=1)

        elif datetime.utcnow() - expires_at < timedelta(minutes=5):
            raise InvitesExceptions.TooShortLifespan("Invite must live at least 5 minutes")

        if users_limit < 1:
            raise InvitesExceptions.InvalidUsersLimitValue(
                "You must have at least 1 participant being able to use invite"
            )

        new_invite = GroupInvite(
            created_by_participant_id=created_by_participant_id,
            group_channel_id=group_channel_id,
            expires_at=expires_at,
            users_limit=users_limit
        )
        await session.commit()

        return new_invite
