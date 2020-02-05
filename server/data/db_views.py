import peewee
from enum import Enum

if __name__ != "__main__":
    from data.config import db_engine
else:
    from config import db_engine
#temporaly sync version


class ChatType(Enum):
    private_dm = 0
    dm = 1
    group_dm = 2
    server_channel = 3
    category_channel = 4
    voice_channel = 5


class RolesPermission(Enum):
    owner = 1 << 31
    admin = 1 << 30
    manage_server = 1 << 29
    manage_channels = 1 << 28
    ban_users = 1 << 27
    kick_users = 1 << 26
    deaf_users = 1 << 25
    mute_users = 1 << 24
    manage_nicknames = 1 << 23
    manage_roles = 1 << 22
    manage_messages = 1 << 13
    view_log = 1 << 21
    view_channel = 1 << 20
    read_messages = 1 << 20
    send_messages = 1 << 19
    change_nicknames = 1 << 18
    create_invites = 1 << 17
    connect = 1 << 16
    speak = 1 << 15
    mention_everyone = 1 << 14


class Status(Enum):
    offline = 0
    online = 1
    away = 2
    dnd = 3
    fake_offline = 4

# TODO: deal with a fricking crap around foreign keys which giving me more pain in the ass
# than profic and also not working how expected from docs
class User(peewee.Model):
    id = peewee.IntegerField(unique=True, primary_key=True)
    bot = peewee.BooleanField(default=False)
    status = peewee.IntegerField(default=0)
    #avatar has same id as user do
    username = peewee.CharField(max_length=50)
    token = peewee.TextField(unique=True)

    #do not use these two as only indentifiers
    #passwords can be not unique
    login = peewee.TextField(unique=True)
    password = peewee.TextField()


    class Meta:
        database = db_engine

class Member(peewee.Model):
    origin = peewee.ForeignKeyField(User)
    nick = peewee.CharField(50)
    roles = []
    deaf, mute = peewee.BooleanField(default=False), peewee.BooleanField(default=False)


    class Meta:
        database = db_engine


class Channel:
    id = peewee.IntegerField(unique=True, primary_key=True)
    channel_type = peewee.IntegerField(default=ChatType.dm)
    origin = peewee.IntegerField() #getting origin by its id and chat type
    position = peewee.IntegerField(null=True)
    overwrites = []
    name = peewee.CharField(50)
    topic = peewee.TextField(null=True)
    nsfw = peewee.BooleanField(default=False)
    #icon again can be gotten using id
    # owner = peewee.ForeignKeyField(Member)
    # members = peewee.ForeignKeyField(Member)

    class Meta:
        database = db_engine

class Server:
    # channels = peewee.ForeignKeyField(Channel)
    # members = peewee.ForeignKeyField(Member)

    class Meta:
        database = db_engine