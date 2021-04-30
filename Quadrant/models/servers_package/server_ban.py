from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, UniqueConstraint, select
from sqlalchemy.orm import relationship
from sqlalchemy.exc import NoResultFound

from Quadrant import models
from Quadrant.models import Base
from Quadrant.models.group_channel_package.group_ban import BANS_PER_PAGE


class ServerBan(Base):
    id = Column(BigInteger, primary_key=True)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False, index=True)
    banned_user_id = Column(ForeignKey('users_package.id'), nullable=False)
    banned_by_user_id = Column(ForeignKey("users_package.id"), nullable=False, index=True)
    banned_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String(2048), default="")

    banned_user = relationship(
        "User", lazy='joined', primaryjoin="ServerBan.banned_user_id == User.id", uselist=False
    )
    banned_by = relationship(
        "User", lazy="joined", primaryjoin="ServerBan.banned_by_user_id == User.id", uselist=False
    )
    __table_args__ = (
        UniqueConstraint("server_id", "banned_user_id", name="_unique_ban_from_server"),
    )

    @staticmethod
    def get_ban_query(server_id: UUID, banned_user_id: models.User.id):
        return select(ServerBan).filter(
            ServerBan.server_id == server_id,
            ServerBan.banned_user_id == banned_user_id
        )

    @classmethod
    async def get_ban(cls, server_id: UUID, banned_user_id: models.User.id, *, session):
        query_result = await session.execute(
            cls.get_ban_query(server_id, banned_user_id)
        )
        return await query_result.one()

    @classmethod
    async def is_user_banned(cls, server_id: UUID, banned_user_id: models.User.id, *, session) -> bool:
        try:
            await cls.get_ban(server_id, banned_user_id, session=session)

        except NoResultFound:
            return False

        return True

    @staticmethod
    async def get_bans_page(server_id: UUID, page: int = 0, *, session):
        if page < 0:
            raise ValueError("Invalid page number")

        query_result = await session.execute(
            select(ServerBan)
            .filter(ServerBan.server_id == server_id).order_by(
                ServerBan.banned_user_id.desc()
            ).limit(BANS_PER_PAGE).offset(page * BANS_PER_PAGE)
        )

        return await query_result.all()
