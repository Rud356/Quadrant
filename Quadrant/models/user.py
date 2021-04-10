from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import uuid4, UUID

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, and_
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa
from sqlalchemy.exc import NoResultFound

from .db_init import Base
from .users_status import UsersStatus
from .settings import UsersCommonSettings, UsersAppSpecificSettings
from .utils import generate_random_color
from .caching import FromCache, RelationshipCache

MAX_OWNED_BOTS = 20


class User(Base):
    id = Column(db_UUID, primary_key=True, default=uuid4)
    color_id = Column(Integer, default=generate_random_color, nullable=False)
    username = Column(String(length='50'), nullable=False)
    status = Column(Enum(UsersStatus), default=UsersStatus.online, nullable=False)
    text_status = Column(String(256), nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    is_bot = Column(Boolean, nullable=False, default=False)
    is_banned = Column(Boolean, nullable=False, default=False)

    bot_owner_id = Column(db_UUID, nullable=True)
    users_common_settings = relationship(UsersCommonSettings, lazy='joined', uselist=False)

    __tablename__ = "users"

    async def update_user(self, *, fields: dict, session) -> None:
        updatable_fields = {"username", "status", "text_status"}

        for updatable_field in updatable_fields:
            if updatable_field in fields:
                # Apply validators
                setattr(self, updatable_field, fields[updatable_field])

        await session.commit()

    async def set_status(self, status: str, *, session) -> None:
        # Raises KeyError if there's no such status in enum
        status = UsersStatus[status]
        self.status = status
        await session.commit()

    async def set_text_status(self, text_status: str, *, session) -> None:
        self.text_status = text_status
        await session.commit()

    async def get_owned_bot(self, bot_id: int, *, session) -> User:
        try:
            bot = await session.query(User).options(FromCache("default")).filter(
                and_(User.is_bot.is_(True), User.bot_owner_id == self.id, User.id == bot_id)
            ).one()

        except OverflowError:
            raise NoResultFound("Bot with that id not found")

        return bot

    async def get_owned_bots(self, *, session) -> List[User]:
        if self.is_bot:
            raise ValueError("Bots can't own other bots")

        bots = await session.query(User).filter(
            and_(User.is_bot.is_(True), User.bot_owner_id == self.id)
        ).limit(MAX_OWNED_BOTS).order_by(User.registered_at.desc()).all()

        return bots

    async def get_app_specific_settings(self, app_id: str, *, session) -> UsersAppSpecificSettings:
        return await UsersAppSpecificSettings.get_app_specific_settings(self, app_id, session=session)

    @classmethod
    async def get_user(cls, user_id: UUID, *, session, filter_deleted: bool = True, filter_bots: bool = False):
        user_query = session.query(cls) \
            .options(FromCache("default")) \
            .options(RelationshipCache(cls.users_common_settings, "default")) \
            .filter(cls.id == user_id)
        if filter_deleted:
            user_query = user_query.filter(cls.is_banned.is_(False))

        if filter_bots:
            user_query = user_query.filter(cls.is_bot.is_(False))

        user = await user_query.one()

        return user
