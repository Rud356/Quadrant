from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, func, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

from Quadrant.models import Base, users_package
from .group_ban import GroupBan
from .group_invite import GroupInvite
from .group_message import GroupMessage
from .group_participant import GroupParticipant

MAX_GROUP_MEMBERS_COUNT = 10


class GroupMessagesChannel(Base):
    channel_id: Mapped[UUID] = Column(db_UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    channel_name: Mapped[str] = Column(String(50), default="Untitled text channel")
    owner_id: Mapped[UUID] = Column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    members: Mapped[List[GroupParticipant]] = relationship(
        GroupParticipant, lazy='joined', cascade="all, delete-orphan"
    )

    # They will never likely be loaded
    _bans: Optional[GroupBan] = relationship(GroupBan, lazy='noload', cascade="all, delete-orphan")
    _messages: Optional[GroupMessage] = relationship(GroupMessage, lazy="noload", cascade="all, delete-orphan")
    _invites: Optional[GroupInvite] = relationship(GroupInvite, lazy='noload', cascade="all, delete-orphan")

    __tablename__ = "group_channels"

    async def leave_group(self, user_leaving: users_package.User, *, session) -> None:
        member = self.members.filter(GroupParticipant.user_id == user_leaving.id).scalar_one()
        self.members.remove(member)
        await session.commit()

    async def kick_member(self, kicked_by: users_package.User, kicking_user: GroupParticipant, *, session) -> None:
        if kicked_by.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        if kicking_user == kicked_by.id:
            raise ValueError("User can not kick himself")

        member = self.members.filter(GroupParticipant.user_id == kicking_user).scalar_one()
        self.members.remove(member)
        await session.commit()

    async def ban_member(
        self, banned_by: users_package.User, banning_user: GroupParticipant, reason: str, *, session
    ) -> None:
        if banned_by.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        if banning_user == banned_by.id:
            raise ValueError("User can not ban himself")

        member = self.members.filter(GroupParticipant.user_id == banning_user).scalar_one()
        new_ban = GroupBan(reason=reason, group_id=self.channel_id, banned_user_id=banning_user)

        session.add(new_ban)
        self.members.remove(member)
        await session.commit()

    async def unban_user(self, unban_by: users_package.User, unbanning_user: users_package.User, *, session) -> None:
        if unban_by.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        if unbanning_user == unban_by.id:
            raise ValueError("User can not unban himself")

        ban_instance = GroupBan.get_ban(self.id, unbanning_user.id, session=session)
        session.delete(ban_instance)
        await session.commit()

    async def transfer_ownership(self, user_transferring: users_package.User, other_member_id: UUID, *, session):
        if user_transferring.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        member = await self.members.filter(GroupParticipant.user_id == other_member_id).scalar_one()
        self.owner_id = member.id

        await session.commit()

    async def add_invite(
        self, created_by: GroupParticipant,
        expires_at: Optional[datetime] = None, users_limit: Optional[int] = 1, *, session
    ) -> GroupInvite:
        if created_by.channel_id != self.channel_id:
            raise PermissionError("User isn't a channel member")

        try:
            new_invite = await GroupInvite.new_invite(
                self.channel_id, created_by.user_id,
                expires_at, users_limit, session=session
            )

        except OverflowError:
            raise ValueError("User limit for group invite must be 32 bits number at max")

        return new_invite

    async def delete_invite(self, invite_code: str, participant: GroupParticipant, *, session) -> None:
        if participant.channel_id != self.channel_id:
            raise self.exc.UserIsNotAMemberError("User isn't a channel member")

        invite = await GroupInvite.get_invite_by_code(invite_code, session=session)
        if participant.id != self.owner_id or invite.created_by_participant_id != participant.id:
            raise self.exc.CanNotDeleteInviteError("User can not delete invites")

        if invite.group_channel_id != self.channel_id:
            raise ValueError("Invalid invite id")

        session.delete(invite)
        await session.commit()

    @staticmethod
    async def use_join_via_invite(
        user_joining: users_package.User, invite_code: str, *, session
    ) -> GroupMessagesChannel:
        group_invite: GroupInvite = await GroupInvite.get_invite_by_code(invite_code, session=session)

        # Fetching number of users in channel to not let too many of them into group channel
        group_members_count_query = select(GroupMessagesChannel.members_count).filter(
            GroupMessagesChannel.channel_id == group_invite.group_channel_id
        )
        group_members_count_query_result = await session.execute(group_members_count_query)
        group_members_count = await group_members_count_query_result.scalar()

        if group_members_count >= MAX_GROUP_MEMBERS_COUNT:
            raise GroupMessagesChannel.exc.TooManyUsersError("There's already max number of users in group")

        if await GroupBan.is_user_banned(group_invite.group_channel_id, user_joining.id, session=session):
            raise GroupMessagesChannel.exc.UserIsBannedError("User has been banned")

        if await GroupMessagesChannel.is_member(group_invite.group_channel_id, user_joining, session=session):
            raise GroupMessagesChannel.exc.AlreadyIsMemberError("User already a channel participant")

        new_member = GroupParticipant(user_id=user_joining.id, channel_id=group_invite.group_channel_id)
        group: GroupMessagesChannel = await GroupMessagesChannel.get_group_channel(
            group_invite.group_channel_id, session=session
        )

        group.members.append(new_member)
        group_invite.users_used_invite += 1
        await session.commit()

        return group

    @hybrid_property
    def members_count(self) -> int:
        return self.members.count()

    @members_count.expression
    def members_count(cls):  # noqa
        return select(func.count()).select_from(GroupParticipant).where(
            GroupParticipant.channel_id == cls.channel_id
        )

    @classmethod
    async def get_group_channel(cls, channel_id: UUID, *, session):
        query = select(cls).filter(cls.channel_id == channel_id)
        query_result = await session.execute(query)
        return await query_result.scalar_one()

    @classmethod
    async def create_group_channel(cls, channel_name: str, owner: users_package.User, *, session):
        # TODO: validate text_channel name
        new_group_channel = cls(
            channel_name=channel_name, owner_id=owner.id,
            members=[GroupParticipant(user_id=owner.id)], invites=[GroupInvite()]
        )
        await session.commit()
        return new_group_channel

    async def delete_channel(self, delete_by: users_package.User, *, session) -> bool:
        if delete_by.id != self.owner_id:
            raise PermissionError("User can not delete this group text_channel")

        session.delete(self)
        await session.commit()

        return True

    @staticmethod
    async def is_member(channel_id: UUID, user: users_package.User, *, session) -> bool:
        exists_query = select(GroupParticipant).filter(
            GroupParticipant.user_id == user.id,
            GroupParticipant.channel_id == channel_id
        ).exists()
        exists_query_result = await session.execute(exists_query)

        return (await exists_query_result.scalar()) or False

    class exc:
        class AlreadyIsMemberError(PermissionError):
            pass

        class UserIsBannedError(PermissionError):
            pass

        class TooManyUsersError(ValueError):
            pass

        class UserIsNotAMemberError(PermissionError):
            pass

        class UserIsNotAnOwnerError(PermissionError):
            pass

        class CanNotDeleteInviteError(PermissionError):
            pass
