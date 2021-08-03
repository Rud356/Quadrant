from __future__ import annotations

from math import ceil
from datetime import datetime
from typing import TYPE_CHECKING, Tuple
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, and_, select
from sqlalchemy.orm import Mapped
from sqlalchemy.exc import IntegrityError, NoResultFound

from Quadrant.models.db_init import Base
from Quadrant.quadrant_logging import gen_log

if TYPE_CHECKING:
    from .user import User

SESSIONS_PER_PAGE = 10

# TODO: add ips logging (if user been switching ips)
# TODO: bind users sessions to apps


class UserSession(Base):
    session_id: Mapped[int] = Column(BigInteger, primary_key=True)
    user_id: Mapped[UUID] = Column(ForeignKey("users.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    # Max length of IPv6 address as string
    ip_address: Mapped[str] = Column(String(45), nullable=False)
    is_alive: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    __tablename__ = "users_sessions"

    @staticmethod
    def user_session_query(user_id: UUID):
        """
        Gives prepared base for querying sessions of exact participant with id.

        :param user_id: participant id of one participant, whose sessions we must get.
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

        :param user: participant instance for whom we create session.
        :param ip_address: session ip address from which we got authorization request.
        :param session: sqlalchemy session.
        :return: new participant session.
        """
        user_session = UserSession(user_id=user.id, ip_address=ip_address)
        session.add(user_session)
        session.commit()

        return user_session

    @classmethod
    async def get_alive_user_session(cls, user_id: UUID, session_id: int, *, session):
        """
        Gives exact session.

        :param user_id: participant id of one participant, whose sessions we must get.
        :param session_id: id of exact session.
        :param session: sqlalchemy session.
        :return: session instance.
        """

        try:
            query = cls.user_session_query(user_id=user_id).filter(UserSession.session_id == session_id)
            query_result = await session.execute(query)
            return query_result.scalar_one()

        except (IntegrityError, NoResultFound, OverflowError):
            gen_log.debug(f"Invalid session id or session with that id wasn't found / is not alive -> {session_id}")
            raise ValueError("No such session")

    @classmethod
    async def get_user_session(cls, user_id: UUID, session_id: int, *, session):
        """
        Gives exact session.

        :param user_id: participant id of one participant, whose sessions we must get.
        :param session_id: id of exact session.
        :param session: sqlalchemy session.
        :return: session instance.
        """

        try:
            query = select(UserSession).filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.session_id == session_id
                )
            )
            query_result = await session.execute(query)
            return query_result.scalar_one()

        except (IntegrityError, OverflowError):
            gen_log.debug(f"Invalid session id or session with that id wasn't found -> {session_id}")
            raise ValueError("No such session")

    @classmethod
    async def get_user_sessions_page(cls, user_id: UUID, page: int, *, session) -> Tuple[UserSession]:
        """
        Gives one page of sessions or empty list.

        :param user_id: participant id of one participant, whose sessions we must get.
        :param page: page of sessions.
        :param session: sqlalchemy session.
        :return: session instances tuple.
        """
        if page < 0:
            gen_log.error(f"Invalid page number for session -> {page}")
            raise ValueError("Invalid page")

        try:
            query = select(cls).filter(user_id=user_id) \
                .limit(SESSIONS_PER_PAGE).offset(SESSIONS_PER_PAGE * page) \
                .order_by(cls.is_alive.desc(), cls.session_id.desc())

            query_result = await session.execute(query)
            return query_result.scalars().all()

        except OverflowError:
            gen_log.error(f"Invalid page number for session -> {page}")
            raise ValueError("No such sessions page")

    @staticmethod
    async def get_sessions_pages_count(user_id: UUID, *, session) -> int:
        query = select(UserSession.session_id).filter_by(user_id=user_id, session=session).count()
        query_result = await session.execute(query)
        pages_count = ceil(query_result.scalar() / SESSIONS_PER_PAGE)
        gen_log.debug(f"Pages of session for user {user_id} -> {pages_count}")

        return pages_count

    @staticmethod
    async def terminate_all_sessions(user_id: UUID, *, session) -> bool:
        """
        Terminates all sessions started by that participant. Can be used in case participant got hacked and wants to nullify
        access to his account.

        :param user_id: participant id of one participant, whose sessions we must get
        :param session: sqlalchemy session.
        :return: session instances tuple.
        """
        # TODO: Ensure that sessions are closed after this method
        users_sessions_query = await session.stream(UserSession.user_session_query(user_id))
        async for user_session in users_sessions_query.partitions(10):
            # TODO: add sessions cache
            user_session: UserSession
            user_session.is_alive = False

        gen_log.info(f"Users {user_id} sessions were terminated")
        await session.commit()
        return True

    def as_dict(self):
        return {
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "started_at": self.started_at,
            "is_alive": self.is_alive,
        }

    async def terminate_session(self, *, session) -> None:
        """Kills all users sessions."""
        self.is_alive = False
        gen_log.info(f"Users {self.user_id} session {self.session_id} was terminated")
        await session.commit()
