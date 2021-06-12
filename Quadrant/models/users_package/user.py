from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, and_, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa
from sqlalchemy.orm import relationship

from Quadrant.models.db_init import Base
from Quadrant.models.users_package.settings import UsersAppSpecificSettings, UsersCommonSettings
from Quadrant.models.utils import generate_random_color
from Quadrant.quadrant_logging import gen_log
from .users_status import UsersStatus

MAX_OWNED_BOTS = 20


class User(Base):
    id = Column(db_UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    color_id = Column(Integer, default=generate_random_color, nullable=False)
    username = Column(String(length=50), nullable=False)
    status = Column(Enum(UsersStatus), default=UsersStatus.online, nullable=False)
    text_status = Column(String(length=256), nullable=False, default="")
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    is_bot = Column(Boolean, nullable=False, default=False)
    is_banned = Column(Boolean, nullable=False, default=False)

    bot_owner_id = Column(ForeignKey("users.id"), nullable=True)
    users_common_settings: UsersCommonSettings = relationship(
        UsersCommonSettings, lazy='joined', uselist=False, cascade="all, delete-orphan"
    )
    _owned_bots = relationship("User", cascade="all, delete-orphan", lazy='noload')
    _users_app_specific_settings = relationship(UsersAppSpecificSettings, lazy="noload", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint('color_id', 'username', name='_unique_user_nick_and_color_id'),)
    __tablename__ = "users"

    async def set_username(self, username: str, *, session) -> None:
        """
        Sets participant a new username.

        :param username: new username that was validated on previous stage.
        :param session: sqlalchemy session.
        :return: nothing.
        """
        self.username = username
        await session.commit()

        gen_log.debug(f"User with id {self.id} has updated nickname to {username}")

    async def set_status(self, status: str, *, session) -> None:
        """
        Sets participant a new status.

        :param status: one of string names from Quadrant.models.users_package.users_status.UsersStatus enum.
        :param session: sqlalchemy session.
        :return: nothing.
        """
        # Raises KeyError if there's no such status in enum
        status = UsersStatus[status]
        self.status = status
        await session.commit()

        gen_log.debug(f"{self.id} has updated status to {status}")

    async def set_text_status(self, text_status: str, *, session) -> None:
        """
        Sets participant a new text status.

        :param text_status:
        :param session: sqlalchemy session.
        :return: nothing.
        """
        # TODO: add validations and clean up
        self.text_status = text_status
        await session.commit()

        gen_log.debug(f"User with id {self.id} has updated text status to {text_status}")

    async def get_owned_bot(self, bot_id: UUID, *, session) -> User:
        """
        Gives specific bot that belongs to participant by bots id.

        :param bot_id: bots id that participant wants to get and owns.
        :param session: sqlalchemy session.
        :return: nothing.
        """
        bot_query = select(User).filter(
            and_(
                User.is_bot.is_(True),
                User.bot_owner_id == self.id,
                User.id == bot_id
            )
        )
        result = await session.execute(bot_query)
        bot = result.scalar_one()

        return bot

    async def get_owned_bots(self, *, session) -> List[User]:
        """
        Gives a list of bot users that belong to participant.

        :param session: sqlalchemy session.
        :return: list of User instances, that are bots belonging to requester.
        """
        if self.is_bot:
            gen_log.info(f"Bot with id {self.id} requested his bots list (bots can't own other bots)")
            raise ValueError("Bots can't own other bots")

        bots_query = select(User).filter(
            and_(
                User.is_bot.is_(True),
                User.bot_owner_id == self.id
            )
        ).limit(MAX_OWNED_BOTS).order_by(User.registered_at.desc())
        result = await session.execute(bots_query)
        bots = result.scalars().all()

        gen_log.debug(f"User with id {self.id} got {len(bots)} bots")
        return bots

    async def get_app_specific_settings(self, app_id: str, *, session) -> UsersAppSpecificSettings:
        """
        Gives an instance of settings on specific application that users uses.
        This is basically an key-value storage for participant to have any sort of configs for his apps.

        :param app_id: application id (can be string with max length of 50 and not 0 symbols)
        :param session: sqlalchemy session.
        :return: UsersAppSpecificSettings instance that can be modified if needed.
        """
        settings = await UsersAppSpecificSettings.get_app_specific_settings(self, app_id, session=session)

        if settings is None:
            gen_log.debug(f"App with id {app_id} not found for that participant")

        return settings

    def as_dict(self):
        user_fields = {
            "id": self.id,
            "color_id": self.color_id,
            "username": self.username,
            "status": self.status.name,
            "text_status": self.text_status,
            "registered_at": self.registered_at,
            "is_bot": self.is_bot,
            "is_banned": self.is_banned
        }

        return user_fields

    @classmethod
    async def get_user(
        cls, user_id: UUID, *, session, filter_banned: bool = True, filter_bots: bool = False
    ) -> User:
        """
        Gives an participant by specific id.

        :param user_id: id of participant someone wants to get.
        :param session: sqlalchemy session.
        :param filter_banned: flag that shows if we must include banned users.
        :param filter_bots: flag that shows if we must include bots.
        :return: participant instance.
        """
        user_query = select(cls).filter(cls.id == user_id)

        if filter_banned:
            user_query = user_query.filter(cls.is_banned.is_(False))

        if filter_bots:
            user_query = user_query.filter(cls.is_bot.is_(False))

        # TODO: maybe add option to not fetch users settings
        result = await session.execute(user_query)
        user = result.scalar_one()

        return user

    @classmethod
    async def get_user_by_username_and_color_id(cls, username: str, color_id: int, *, session) -> User:
        user_query = select(cls).filter(
            cls.username == username,
            cls.color_id == color_id,
            cls.is_bot.is_(False),
            cls.is_banned.is_(False)
        )
        result = await session.execute(user_query)
        user = result.scalar_one()

        return user

    class exc:
        class UserIsBot(PermissionError):
            ...
