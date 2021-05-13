from __future__ import annotations

from typing import List, TYPE_CHECKING, Dict, Any
from contextlib import suppress

from sqlalchemy import BigInteger, ForeignKey, Column, and_, or_, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from Quadrant.models.db_init import Base
from Quadrant.models.utils.common_settings_validators import (
    COMMON_SETTINGS, DEFAULT_COMMON_SETTINGS_DICT, CommonSettingsValidator
)

if TYPE_CHECKING:
    from .user import User


class UsersCommonSettings(Base):
    settings_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True, nullable=False)

    common_settings = Column(MutableDict.as_mutable(JSONB), default=DEFAULT_COMMON_SETTINGS_DICT)
    # TODO: make this class use bool values instead of dictionary for easier migrations
    __tablename__ = "users_common_settings"

    async def get_setting(self, key: str, *, session) -> Any:
        """
        Gets exact setting from common settings set.

        :param key: setting key.
        :param session: sqlalchemy session.
        :return: value.
        """
        try:
            return self.common_settings[key]

        except KeyError:
            default_value = DEFAULT_COMMON_SETTINGS_DICT[key]
            self.common_settings[key] = default_value
            await session.commit()
            return default_value

    async def update_settings(self, *, settings: Dict[str, Any], session) -> Dict[str, Dict[str, Any]]:
        """
        Updates settings from common settings list.
        :param settings: dictionary with setting_key: setting_value.
        :param session: sqlalchemy session.
        :return: dictionary containing one key "updated_settings" where has another dict
        with setting_key and its new value.
        """
        # Validate settings values
        updated_settings = {}

        for key in set(settings.keys()) & set(COMMON_SETTINGS.keys()):
            with suppress(ValueError, KeyError):
                validator: CommonSettingsValidator = COMMON_SETTINGS[key]
                value = settings[key]
                validator.validate(value)
                updated_settings[key] = value
                self.common_settings[key] = value

        if not updated_settings:
            raise ValueError("No settings was updated")

        await session.commit()
        return {"updated_settings": updated_settings}


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
        Gives app settings for specific participant.

        :param user: participant instance of the one, who requests those.
        :param app_id: string with max length of 50 symbols.
        :param session: sqlalchemy session.
        :return: instance of app specific settings.
        """
        query = select(cls).filter(cls.user_id == user.id, cls.app_id == app_id)
        query_result = await session.execute(query)
        settings = await query_result.scalar_one()

        return settings
