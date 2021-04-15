from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, func, not_, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

import Quadrant.models
import Quadrant.models.group_channel_package.group_messages
from Quadrant import models
from Quadrant.models import Base, FromCache, RelationshipCache
from Quadrant.models.dm_channel_package.dm_channels import GROUP_MEMBERS_LIMIT


class GroupMessagesChannel(Base):
    channel_id = Column(db_UUID, primary_key=True, default=uuid4)
    channel_name = Column(String(50), default="Untitled text_channel")
    owner_id = Column(ForeignKey("users_package.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship(Quadrant.models.group_channel_models.group_participant.GroupParticipant, lazy='joined', cascade="all, delete-orphan")
    _messages = relationship(Quadrant.models.group_channel.group_messages.GroupMessage, lazy="noload", cascade="all, delete-orphan")
    invites = relationship(
        models.GroupInvite, lazy='joined',
        primaryjoin="""
            and_(
                GroupMessagesChannel.channel_id == models.GroupInvite,
                models.GroupInvite.is_expired.is_(False)
            )
        """, cascade="all, delete-orphan"
    )

    __tablename__ = "group_channels"

    async def leave_group(self, user_leaving: models.User, *, session) -> None:
        member = await self.members.filter(
            Quadrant.models.group_channel_models.group_participant.GroupParticipant.user_id == user_leaving.id).one()
        self.members.remove(member)
        await session.commit()

    async def kick_member(self, kicked_by: models.User, kicking_user: models.User.id, *, session) -> None:
        if kicked_by.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        if kicking_user == kicked_by.id:
            raise ValueError("User can not kick himself")

        member = await self.members.filter(
            Quadrant.models.group_channel_models.group_participant.GroupParticipant.user_id == kicking_user).one()
        self.members.remove(member)
        await session.commit()

    async def ban_member(self, banned_by: models.User, banning_user: models.User.id, reason: str, *, session) -> None:
        if banned_by.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        if banning_user == banned_by.id:
            raise ValueError("User can not ban himself")

        member = await self.members.filter(
            Quadrant.models.group_channel_models.group_participant.GroupParticipant.user_id == banning_user).one()
        models.GroupBans(reason=reason, group_id=self.channel_id, banned_user_id=banning_user)
        self.members.remove(member)

        await session.commit()

    async def unban_user(self, unban_by: models.User, unbanning_user: models.User.id, *, session) -> None:
        if unban_by.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        if unbanning_user == unban_by.id:
            raise ValueError("User can not unban himself")

        ban_instance = models.GroupBans.get_ban(self.id, unbanning_user.id, session=session)
        session.delete(ban_instance)
        await session.commit()

    async def transfer_ownership(self, user_transferring: models.User, other_member_id: UUID, *, session):
        if user_transferring.id != self.owner_id:
            raise PermissionError("User isn't delete_by of group dm")

        member = await self.members.filter(
            Quadrant.models.group_channel_models.group_participant.GroupParticipant.user_id == other_member_id).one()
        self.owner_id = member.id

        await session.commit()

    async def add_invite(
        self, expires_at: Optional[datetime] = None, users_limit: Optional[int] = 1, *, session
    ) -> models.GroupInvite:
        if self.invites.count() > GROUP_MEMBERS_LIMIT:
            raise models.InvitesExceptions.TooManyInvites("Too many invites for dm group")

        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(days=1)

        elif datetime.utcnow() - expires_at < timedelta(minutes=5):
            raise models.InvitesExceptions.TooShortLifespan("Invite must live at least 5 minutes")

        if users_limit < 1:
            raise models.InvitesExceptions.InvalidUsersLimitValue(
                "You must have at least 1 user being able to use invite"
            )

        new_invite = models.GroupInvite(
            group_channel_id=self.channel_id, expires_at=expires_at, users_limit=users_limit
        )

        self.invites.append(new_invite)
        await session.commit()

        return new_invite

    async def delete_invite(self, invite_code: str, user: models.User, *, session) -> None:
        if user.id != self.owner_id:
            raise PermissionError("User can not delete invites")

        invite = await self.invites.filter(models.GroupInvite.invite_code == invite_code).one()
        self.invites.remove(invite)
        await session.commit()

    @staticmethod
    async def use_join_via_invite(user_joining: models.User, invite_code: str, *, session) -> GroupMessagesChannel:
        group_invite: models.GroupInvite = await session.query(models.GroupInvite).filter(
            models.GroupInvite.invite_code == invite_code, not_(models.GroupInvite.is_expired)
        )

        if await models.GroupBans.is_user_banned(group_invite.group_channel_id, user_joining.id, session=session):
            raise PermissionError("User has been banned")

        new_member = models.DMParticipant(user_id=user_joining.id, channel_id=group_invite.group_channel_id)
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
        return select(func.count()).select_from(Quadrant.models.group_channel_models.group_participant.GroupParticipant).where(
            Quadrant.models.group_channel_models.group_participant.GroupParticipant.channel_id == cls.channel_id
        )

    @classmethod
    async def get_group_channel(cls, channel_id: UUID, *, session):
        return await session.query(cls).filter(cls.channel_id == channel_id)\
            .options(FromCache("default")) \
            .options(RelationshipCache(cls.members, "default").and_(RelationshipCache(cls.invites, "default"))) \
            .one()

    @classmethod
    async def create_group_channel(cls, channel_name: str, owner: models.User, *, session):
        # TODO: validate text_channel name
        new_group_channel = cls(
            channel_name=channel_name, owner_id=owner.id,
            members=[Quadrant.models.group_channel_models.group_participant.GroupParticipant(user_id=owner.id)], invites=[models.GroupInvite()]
        )
        await session.commit()
        return new_group_channel

    async def delete_channel(self, delete_by: models.User, *, session) -> bool:
        if delete_by.id != self.owner_id:
            raise PermissionError("User can not delete this group text_channel")

        session.delete(self)
        await session.commit()

        return True

    @staticmethod
    async def is_member(channel_id: UUID, user: models.User, *, session) -> bool:
        return await session.query(
            session.query(Quadrant.models.group_channel_models.group_participant.GroupParticipant).filter(
                Quadrant.models.group_channel_models.group_participant.GroupParticipant.user_id == user.id,
                Quadrant.models.group_channel_models.group_participant.GroupParticipant.channel_id == channel_id
            ).exists()
        ).scalar() or False