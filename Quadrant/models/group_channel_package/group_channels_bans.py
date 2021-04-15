from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Column, ForeignKey, UniqueConstraint, DateTime, String
from sqlalchemy.orm import relationship

from Quadrant import models
from Quadrant.models.db_init import Base
from Quadrant.models.caching import FromCache

BANS_PER_PAGE = 25


class GroupBans(Base):
    id = Column(BigInteger, primary_key=True)
    reason = Column(String(2048), default="")
    group_id = Column(ForeignKey("group_channels.channel_id"), nullable=False, index=True)
    banned_user_id = Column(ForeignKey('users_package.id'), nullable=False)
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
        return await cls.get_ban_query(group_id, banned_user_id, session=session).options(FromCache("default")).one()

    @classmethod
    async def is_user_banned(cls, group_id: UUID, check_user_id: models.User.id, *, session) -> bool:
        return await session.query(
            cls.get_ban_query(group_id, check_user_id, session=session).exists()
        ).options(FromCache("default")).scalar()

    @staticmethod
    async def get_bans_page(group_id: UUID, page: int = 0, *, session):
        if page < 0:
            raise ValueError("Invalid page number")

        return await session.query(GroupBans).filter(GroupBans.group_id == group_id).order_by(
            GroupBans.banned_user_id.desc()
        ).limit(BANS_PER_PAGE).offset(page * BANS_PER_PAGE).all()
