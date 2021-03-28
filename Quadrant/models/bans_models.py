from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Column, ForeignKey, UniqueConstraint, DateTime, String
from sqlalchemy.orm import relationship

from Quadrant import models
from .db_init import Base

BANS_PER_PAGE = 25


class GroupBans(Base):
    id = Column(BigInteger, primary_key=True)
    reason = Column(String(2048), default="")
    group_id = Column(ForeignKey("group_channels.channel_id"), nullable=False, index=True)
    banned_user_id = Column(ForeignKey('users.id'), nullable=False)
    banned_at = Column(DateTime, default=datetime.utcnow)

    banned_user = relationship("User", lazy='joined', uselist=False)
    __table_args__ = (
        UniqueConstraint("server_id", "banned_user_id", name="_unique_ban_from_group"),
    )

    @staticmethod
    def get_ban_query(group_id: UUID, banned_user_id: models.User.id, *, session):
        return session.query(GroupBans).filter(
            GroupBans.group_id == group_id, GroupBans.banned_user_id == banned_user_id
        )

    @classmethod
    async def get_ban(cls, group_id: UUID, banned_user_id: models.User.id, *, session):
        return await cls.get_ban_query(group_id, banned_user_id, session=session).one()

    @classmethod
    async def is_user_banned(cls, group_id: UUID, check_user_id: models.User.id, *, session) -> bool:
        return await session.query(
            cls.get_ban_query(group_id, check_user_id, session=session).exists()
        ).scalar()

    @staticmethod
    async def get_bans_page(group_id: UUID, page: int = 0, *, session):
        if page < 0:
            raise ValueError("Invalid page number")

        return await session.filter(GroupBans.group_id == group_id).order_by(
            GroupBans.banned_user_id.desc()
        ).limit(BANS_PER_PAGE).offset(page * BANS_PER_PAGE).all()


class ServerBans(Base):
    id = Column(BigInteger, primary_key=True)
    server_id = Column(ForeignKey("servers.id"), nullable=False, index=True)
    banned_user_id = Column(ForeignKey('users.id'), nullable=False)
    banned_by_user_id = Column(ForeignKey("servers.id"), nullable=False, index=True)
    banned_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String(2048), default="")

    banned_user = relationship("User", lazy='joined', primaryjoin="ServerBans.banned_user_id = User.id", uselist=False)
    banned_by = relationship("User", lazy="joined", primaryjoin="ServerBans.banned_by_user_id = User.id", uselist=False)
    __table_args__ = (
        UniqueConstraint("server_id", "banned_user_id", name="_unique_ban_from_server"),
    )

    @staticmethod
    def get_ban_query(server_id: UUID, banned_user_id: models.User.id, *, session):
        return session.query(ServerBans).filter(
            ServerBans.server_id == server_id, ServerBans.banned_user_id == banned_user_id
        )

    @classmethod
    async def get_ban(cls, server_id: UUID, banned_user_id: models.User.id, *, session):
        return await cls.get_ban_query(server_id, banned_user_id, session=session).one()

    @classmethod
    async def is_user_banned(cls, server_id: UUID, banned_user_id: models.User.id, *, session) -> bool:
        return await session.query(
            cls.get_ban_query(server_id, banned_user_id, session=session).exists()
        ).scalar()

    @staticmethod
    async def get_bans_page(server_id: UUID, page: int = 0, *, session):
        if page < 0:
            raise ValueError("Invalid page number")

        return await session.filter(ServerBans.server_id == server_id).order_by(
            ServerBans.banned_user_id.desc()
        ).limit(BANS_PER_PAGE).offset(page * BANS_PER_PAGE).all()
