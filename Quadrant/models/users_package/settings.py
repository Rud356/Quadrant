from __future__ import annotations

from typing import Any, Callable, Dict, TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from Quadrant.models.db_init import Base

if TYPE_CHECKING:
    from .user import User


class UsersCommonSettings(Base):
    user_id = Column(ForeignKey('users.id'), primary_key=True)

    enable_sites_preview = Column(Boolean, default=False)

    settings_keys = {"enable_sites_preview", }
    KEYS_TO_VALIDATORS = {
        "enable_sites_preview": lambda v: isinstance(v, bool),
    }
    __tablename__ = "users_common_settings"

    async def get_setting(self, key: str) -> Any:
        """
        Gets exact setting from common_variables settings set.

        :param key: setting key.
        :return: value.
        """
        if key not in self.settings_keys:
            raise ValueError("Invalid key")

        return getattr(self, key)

    async def update_settings(
        self, *, settings: Dict[str, Any], session
    ) -> Dict[str, Dict[str, Any]]:
        """
        Updates settings from common_variables settings list.
        :param settings: dictionary with setting_key: setting_value.
        :param session: sqlalchemy session.
        :return: dictionary containing one key "updated_settings" where has another dict
        with setting_key and its new value.
        """
        # Validate settings values
        updated_settings = {}

        for key in set(settings.keys()) & self.settings_keys:
            validator: Callable = self.KEYS_TO_VALIDATORS[key]
            value = settings[key]

            if validator(value):
                updated_settings[key] = value
                setattr(self, key, value)

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
