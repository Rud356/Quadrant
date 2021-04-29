from __future__ import annotations

from typing import List, TYPE_CHECKING
from contextlib import suppress

from sqlalchemy import BigInteger, ForeignKey, Column, and_, or_, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from Quadrant.models.db_init import Base
from Quadrant.models.utils.common_settings_validators import COMMON_SETTINGS, DEFAULT_COMMON_SETTINGS_DICT
from Quadrant.models.caching import FromCache

if TYPE_CHECKING:
    from .user import User


class UsersCommonSettings(Base):
    settings_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True, nullable=False)

    common_settings = Column(MutableDict.as_mutable(JSONB), default=DEFAULT_COMMON_SETTINGS_DICT)

    __tablename__ = "users_common_settings"

    async def get_setting(self, key: str, *, session):
        try:
            return self.common_settings[key]

        except KeyError:
            default_value = DEFAULT_COMMON_SETTINGS_DICT[key]
            self.common_settings[key] = default_value
            await session.commit()
            return default_value

    async def update_settings(self, *, settings: dict, session) -> dict:
        # Validate settings values
        updated_settings = {}

        for settings_validator in COMMON_SETTINGS:
            with suppress(ValueError, KeyError):
                value = settings[settings_validator.key]
                settings_validator.validate(value)
                self.common_settings[settings_validator.key] = value

        if not updated_settings:
            raise ValueError("No settings was updated")

        await session.commit()
        return {"updated_settings": tuple(updated_settings.keys())}


class UsersAppSpecificSettings(Base):
    """
    Class that helps users create and change settings for their apps and sync them through cloud.
    """
    settings_id = Column(BigInteger, primary_key=True)
    app_id = Column(String(length=50), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id'), index=True, nullable=False)

    app_specific_settings = Column(MutableDict.as_mutable(JSONB), default={})
    __tablename__ = "users_app_specific_settings"

    @classmethod
    async def get_app_specific_settings(cls, user: User, app_id: str, *, session):
        """
        Gives app settings for specific user.

        :param user: user instance of the one, who requests those.
        :param app_id: string with max length of 50 symbols.
        :param session: sqlalchemy session.
        :return: instance of app specific settings.
        """
        settings = await (
            await session.execute(
                select(cls).options(FromCache("users_app_settings"))
                .filter(cls.user_id == user.id, cls.app_id == app_id)
            )
        ).one()

        return settings
