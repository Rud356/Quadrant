from __future__ import annotations

from math import ceil
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, relationship

from Quadrant.models import users_package
from Quadrant.models.db_init import AsyncSession, Base

if TYPE_CHECKING:
    from Quadrant.models.users_package import User

BANS_PER_PAGE = 25


class GroupBan(Base):
    id: Mapped[int] = Column(BigInteger, primary_key=True)
    reason: Mapped[str] = Column(String(2048), default="")
    group_id: Mapped[UUID] = Column(ForeignKey("group_channels.channel_id"), nullable=False, index=True)
    banned_user_id: Mapped[UUID] = Column(ForeignKey('users.id'), nullable=False)
    banned_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)

    banned_user: User = relationship("User", lazy='joined', uselist=False)
    __table_args__ = (
        UniqueConstraint("group_id", "banned_user_id", name="_unique_ban_from_group"),
    )
    __tablename__ = "group_bans"

    @staticmethod
    def get_ban_query(group_id: UUID, banned_user_id: users_package.User.id):
        return select(GroupBan).filter(
            GroupBan.group_id == group_id,
            GroupBan.banned_user_id == banned_user_id
        )

    @classmethod
    async def get_ban(
        cls, group_id: UUID, banned_user_id: users_package.User.id, *, session: AsyncSession
    ) -> Optional[GroupBan]:
        query_result = await session.execute(
            cls.get_ban_query(group_id, banned_user_id)
        )

        return await query_result.scalar_one()

    @staticmethod
    async def is_user_banned(
        group_id: UUID, user_id: users_package.User.id, *, session: AsyncSession
    ) -> bool:
        """
        Checks if user is banned in this specific group.

        :param group_id: group channel id where we check if user is banned.
        :param user_id: user id whom we check if he's banned.
        :param session: sqlalchemy session.
        :return: bool value, representing if user is banned.
        """
        query = select(GroupBan.id).filter(
            GroupBan.group_id == group_id,
            GroupBan.banned_user_id == user_id
        ).exists()
        result = await session.execute(query)  # noqa: exists is a valid for query
        return result.scalar() or True

    @staticmethod
    async def get_bans_page(
        group_id: UUID, page: int = 0, *, session: AsyncSession
    ) -> List[GroupBan]:
        """
        Gives a page of bans in this specific group.

        :param group_id: group from which we obtain page.
        :param page: what page we are looking for.
        :param session: sqlalchemy session.
        :return: list of bans.
        """
        if page < 0:
            raise ValueError("Invalid page number")

        query_result = await session.execute(
            select(GroupBan).filter(GroupBan.group_id == group_id).order_by(
                GroupBan.banned_user_id.desc()
            ).limit(BANS_PER_PAGE).offset(page * BANS_PER_PAGE)
        )

        return query_result.scalars().all()

    @staticmethod
    async def total_bans_pages(group_id: UUID, *, session: AsyncSession) -> int:
        """
        Gives a number of pages with banned users for this group.

        :param group_id: group from which we obtain pages count.
        :param session: sqlalchemy session.
        :return: number of pages.
        """
        query_result = await session.execute(
            select(GroupBan.id).filter(  # noqa: count does exists for select
                GroupBan.group_id == group_id
            ).count()
        )
        pages = ceil(query_result.scalar() / BANS_PER_PAGE)
        return pages