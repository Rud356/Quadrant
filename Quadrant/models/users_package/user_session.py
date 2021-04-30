from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Tuple
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, select
from sqlalchemy.exc import IntegrityError

from Quadrant.models.caching import FromCache, caching_environment
from Quadrant.models.db_init import Base

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

    __tablename__ = "users_sessions"

    @staticmethod
    def user_session_query(user_id: UUID):
        """
        Gives prepared base for querying sessions of exact user with id.

        :param user_id: user id of one user, whose sessions we must get.
        :return: sqlalchemy query.
        """
        return select(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_alive.is_(True)
        )

    @classmethod
    async def new_session(cls, user: User, ip_address: str, *, session):
        """
        Creates new session.

        :param user: user instance for whom we create session.
        :param ip_address: session ip address from which we got authorization request.
        :param session: sqlalchemy session.
        :return: new user session.
        """
        user_session = UserSession(user_id=user.id, ip_address=ip_address)
        session.add(user_session)
        session.commit()

        return user_session

    @classmethod
    async def get_user_session(cls, user_id: UUID, session_id: int, *, session):
        """
        Gives exact session.

        :param user_id: user id of one user, whose sessions we must get.
        :param session_id: id of exact session.
        :param session: sqlalchemy session.
        :return: session instance.
        """

        try:
            query = cls.user_session_query(user_id=user_id).filter(UserSession.session_id == session_id)
            query_result = await session.execute(query)
            return await query_result.one()

        except (IntegrityError, OverflowError):
            raise ValueError("No such session")

    @classmethod
    async def get_user_sessions_page(cls, user_id: UUID, page: int, *, session) -> Tuple[UserSession]:
        """
        Gives one page of sessions or empty list.

        :param user_id: user id of one user, whose sessions we must get.
        :param session: sqlalchemy session.
        :return: session instances tuple.
        """
        if page < 0:
            raise ValueError("Invalid page")

        try:
            query = select(cls).filter(user_id=user_id, session=session) \
                .limit(SESSIONS_PER_PAGE).offset(SESSIONS_PER_PAGE * page) \
                .order_by(cls.is_alive.desc(), cls.session_id.desc())

            query_result = await session.execute(query)
            return await query_result.all()

        except (IntegrityError, OverflowError):
            raise ValueError("No such session")

    @staticmethod
    async def terminate_all_sessions(user_id: UUID, *, session) -> bool:
        """
        Terminates all sessions started by that user. Can be used in case user got hacked and wants to nullify
        access to his account.

        :param user_id: user id of one user, whose sessions we must get
        :param session: sqlalchemy session.
        :return: session instances tuple.
        """
        # TODO: Ensure that sessions are closed after this method
        users_sessions_query = await session.stream(UserSession.user_session_query(user_id))
        async for user_session in users_sessions_query.partitions(10):
            user_session: UserSession
            user_session.is_alive = False

        await session.commit()
        return True

    async def terminate_session(self, *, session) -> None:
        self.is_alive = False
        await session.commit()
