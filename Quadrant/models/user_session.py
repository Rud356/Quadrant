from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, BigInteger, DateTime, String, ForeignKey, Boolean
from sqlalchemy.exc import IntegrityError

from uuid import UUID
from .db_init import Base
from .caching import FromCache
from .caching.caching_environment import cache

if TYPE_CHECKING:
    from .user import User

SESSIONS_PER_PAGE = 10


class UserSession(Base):
    session_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey("users.id"), index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    # Max length of IPv6 address as string
    ip_address = Column(String(45))
    is_alive = Column(Boolean, default=True)

    @staticmethod
    def user_session_query(user_id: UUID, *, session):
        return session.query(UserSession).filter(
            UserSession.user_id == user_id, UserSession.is_alive.is_(True)
        ).options(FromCache("default"))

    @classmethod
    async def new_session(cls, user: User, ip_address: str, *, session):
        user_session = UserSession(user_id=user.id, ip_address=ip_address)
        session.add(user_session)
        session.commit()

        return user_session

    @classmethod
    async def get_user_session(cls, user_id: UUID, session_id: int, *, session):
        try:
            return await cls.user_session_query(
                user_id=user_id, session=session
            ).filter(cls.session_id == session_id).one()

        except (IntegrityError, OverflowError):
            raise ValueError("No such session")

    @classmethod
    async def get_user_sessions_page(cls, user_id: UUID, page: int, *, session):
        if page < 0:
            raise ValueError("Invalid page")

        try:
            return await session.query(cls).filter(
                user_id=user_id, session=session
            ).limit(SESSIONS_PER_PAGE).offset(SESSIONS_PER_PAGE * page).order_by(
                cls.is_alive.desc(), cls.session_id.desc()
            ).all()

        except (IntegrityError, OverflowError):
            raise ValueError("No such session")

    @staticmethod
    async def terminate_all_sessions(user_id: UUID, *, session) -> bool:
        # TODO: Ensure that sessions are closed after this method
        async for user_session in UserSession.user_session_query(user_id, session=session).partitions(10):
            user_session: UserSession
            user_session.is_alive = False

        await session.commit()
        return True

    async def terminate_session(self, *, session) -> None:
        self.is_alive = False
        await session.commit()
