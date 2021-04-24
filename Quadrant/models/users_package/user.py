from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import uuid4, UUID

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, and_, select
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa

from Quadrant.models.db_init import Base
from .users_status import UsersStatus
from Quadrant.models.users_package.settings import UsersCommonSettings, UsersAppSpecificSettings
from Quadrant.models.utils import generate_random_color
from Quadrant.models.caching import FromCache, RelationshipCache

MAX_OWNED_BOTS = 20


class User(Base):
    id = Column(db_UUID, primary_key=True, default=uuid4, unique=True)
    color_id = Column(Integer, default=generate_random_color, nullable=False)
    username = Column(String(length=50), nullable=False)
    status = Column(Enum(UsersStatus), default=UsersStatus.online, nullable=False)
    text_status = Column(String(256), nullable=False, default="")
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    is_bot = Column(Boolean, nullable=False, default=False)
    is_banned = Column(Boolean, nullable=False, default=False)

    bot_owner_id = Column(db_UUID, nullable=True)
    users_common_settings: UsersCommonSettings = relationship(
        UsersCommonSettings, lazy='joined', uselist=False, cascade="all, delete-orphan"
    )
    _owned_bots = relationship(
        "User", primaryjoin="and_(User.is_bot.is_(True), User.id == User.bot_owner_id)",
        cascade="all, delete-orphan", lazy='noload'
    )
    _users_app_specific_settings = relationship(UsersAppSpecificSettings, lazy="noload", cascade="all, delete-orphan")

    __tablename__ = "users"

    async def set_username(self, username: str, *, session) -> None:
        # TODO: add validations and clean up
        self.username = username
        await session.commit()

    async def set_status(self, status: str, *, session) -> None:
        # Raises KeyError if there's no such status in enum
        status = UsersStatus[status]
        self.status = status
        await session.commit()

    async def set_text_status(self, text_status: str, *, session) -> None:
        # TODO: add validations and clean up
        self.text_status = text_status
        await session.commit()

    async def get_owned_bot(self, bot_id: UUID, *, session) -> User:
        bot_query = select(User).options(FromCache("default")).filter(
            and_(
                User.is_bot.is_(True),
                User.bot_owner_id == self.id,
                User.id == bot_id
            )
        )
        result = await session.execute(bot_query)
        bot = await result.one()

        return bot

    async def get_owned_bots(self, *, session) -> List[User]:
        if self.is_bot:
            raise ValueError("Bots can't own other bots")
        bots_query = select(User).options(FromCache("default")).filter(
            and_(
                User.is_bot.is_(True),
                User.bot_owner_id == self.id
            )
        ).limit(MAX_OWNED_BOTS).order_by(User.registered_at.desc())
        result = await session.execute(bots_query)
        bots = await result.all()

        return bots

    async def get_app_specific_settings(self, app_id: str, *, session) -> UsersAppSpecificSettings:
        return await UsersAppSpecificSettings.get_app_specific_settings(self, app_id, session=session)

    @classmethod
    async def get_user(
        cls, user_id: UUID, *, session, filter_deleted: bool = True, filter_bots: bool = False
    ) -> User:
        user_query = (
            select(cls).options(FromCache("default"))
            .filter(cls.id == user_id)
        )

        if filter_deleted:
            user_query = user_query.filter(cls.is_banned.is_(False))

        if filter_bots:
            user_query = user_query.filter(cls.is_bot.is_(False))

        result = await session.execute(user_query)
        user = await result.one()

        return user
