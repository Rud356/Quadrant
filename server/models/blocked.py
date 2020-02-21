import peewee
from models.conf import db_engine
from models.user import UserModel
from models.friends import FriendList

class BlockedList(peewee.Model):
    blocked_by = peewee.ForeignKeyField(
        UserModel, backref='+'
    )
    blocked = peewee.ForeignKeyField(
        UserModel, backref='blocked'
    )

    class Meta:
        database = db_engine