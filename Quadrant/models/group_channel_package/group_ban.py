from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship

from Quadrant.models import users_package
from Quadrant.models.caching import FromCache
from Quadrant.models.db_init import Base

BANS_PER_PAGE = 25


class GroupBan(Base):
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
    def get_ban_query(group_id: UUID, banned_user_id: users_package.User.id):
        return select(GroupBan).filter(
            GroupBan.group_id == group_id,
            GroupBan.banned_user_id == banned_user_id
        )

    @classmethod
    async def get_ban(cls, group_id: UUID, banned_user_id: users_package.User.id, *, session) -> Optional[GroupBan]:
        query_result = await session.execute(
            cls.get_ban_query(group_id, banned_user_id).options(FromCache("default"))
        )

        return await query_result.one()

    @staticmethod
    async def is_user_banned(group_id: UUID, user_id: users_package.User.id, *, session) -> bool:
        try:
            # If user is banned - we can obtain ban information (most likely from cache)
            await GroupBan.get_ban(group_id, user_id, session=session)
            return True

        except NoResultFound:
            return False

    @staticmethod
    async def get_bans_page(group_id: UUID, page: int = 0, *, session):
        if page < 0:
            raise ValueError("Invalid page number")

        query_result = await session.execute(
            select(GroupBan).filter(GroupBan.group_id == group_id).order_by(
                GroupBan.banned_user_id.desc()
            ).limit(BANS_PER_PAGE).offset(page * BANS_PER_PAGE)
        )

        return await query_result.all()
