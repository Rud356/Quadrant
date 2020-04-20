from enum import IntEnum

from app import db, session
from sqlalchemy import (
    Column,
    BigInteger, Enum, ForeignKey,
    and_, or_
)


class Setting(IntEnum):
    allow_friend_requests = 1


class UserSettings(db.Model):
    id = Column(ForeignKey('users.id'))
    #TODO: change default value
    settings = Column(BigInteger, default=0)

    def delete_settings(self):
        query = UserSettings.select().filter(
            UserSettings.id==self.id
        )
        session.delete(query)
        session.commit()

    def check_setting(self, setting: int):
        return bool(self.settings & setting)