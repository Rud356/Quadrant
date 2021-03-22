from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Column, and_, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

from .db_init import Base
from .utils.common_settings_validators import COMMON_SETTINGS

if TYPE_CHECKING:
    from .user_model import User


class UsersSettings(Base):
    settings_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), index=True, nullable=False)

    common_settings = Column(MutableDict.as_mutable(JSONB), default={})
    app_specific_settings = Column(MutableDict.as_mutable(JSONB), default={})

    @staticmethod
    async def get_common_settings(user: User, *, session) -> dict:
        common_settings = await session.query(UsersSettings.common_settings) \
            .filter(UsersSettings.user_id == user.id).one_or_none()

        return common_settings or {}

    @staticmethod
    async def get_app_specific_settings(user: User, app: str, *, session) -> dict:
        apps_settings = await session.query(UsersSettings.app_specific_settings[app]) \
            .filter(UsersSettings.user_id == user.id).one_or_none()

        return apps_settings or {}

    @staticmethod
    async def update_common_settings(user: User, *, settings: dict, session) -> dict:
        # Validate settings values
        updated_settings = {}

        for settings_validator in COMMON_SETTINGS:
            try:
                value = settings[settings_validator.key]
                settings_validator.validate(value)

            except (ValueError, KeyError):
                continue

        if not updated_settings:
            raise ValueError("No settings was updated")

        session.query(UsersSettings.common_settings) \
            .filter(UsersSettings.user_id == user.id).update(updated_settings)

        await session.commit()
        return {"updated_settings": tuple(updated_settings.keys())}

    @staticmethod
    async def update_app_specific_settings(user: User, app: str, *, settings: dict, session) -> dict:
        updated_settings = {}

        for settings_validator in COMMON_SETTINGS:
            try:
                value = settings[settings_validator.key]
                settings_validator.validate(value)

            except (ValueError, KeyError):
                continue

        if not updated_settings:
            raise ValueError("No settings was updated")

        session.query(UsersSettings.app_specific_settings[app]) \
            .filter(UsersSettings.user_id == user.id).update(updated_settings)

        await session.commit()
        return {"updated_settings": tuple(updated_settings.keys())}

    @staticmethod
    async def delete_app_specific_setting(user: User, app: str, *, setting: str, session):
        session.query(UsersSettings.app_specific_settings[app][setting]) \
            .filter(UsersSettings.user_id == user.id).delete()

        await session.commit()
