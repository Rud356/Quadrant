import json

clients = {}

class users:
    HEADER_SIZE = 6
    __slots__ = (
        'reader', 'writer',
        'id', 'nick', 'avatar',
        'friends', 'servers', 'channels',
        'blocked', 'status', 'keychain'
    )
    def __init__(
        self, reader, writer, keychain,
        id, nick, avatar,
        friends, servers, channels, blocked, status
        ):

        self.reader, self.writer = reader, writer
        self.keychain = keychain
        self.id = id
        self.nick = nick
        self.avatar = avatar
        self.servers = servers
        self.channels = channels
        self.blocked = blocked
        self.status = status

    async def clear_data(self):
        pass #plaseholder for decrypting data and parsing as json

    async def run_handler(self):
        while True:
            try: header = int(await self.reader(users.HEADER_SIZE).decode())
            except TypeError: continue
            data = await self.reader(header)

    @staticmethod
    async def authorize(login, password):
        #SQL queries to db
        pass

    @classmethod
    async def registrate_user(cls, reader, writer, keychain):
        header = int(await reader.read(users.HEADER_SIZE).decode())
        # decrypt data
        login, password = await reader.read(header).decode().split(' -> ', 1)[:2]
        authorization = users.authorize(login, password)
        if not authorization: writer.write(f'{3:<users.HEADER_SIZE}403'); await writer.drain() #incorrect password or login
        else: return cls(
            reader, writer, keychain, pass
        ) #! write somehow simpler user creationg

# echo client down below
class users_s:
    HEADER_SIZE = 16
    __slots__ = (
        'reader', 'writer',
        'id', 'nick', 'avatar',
        'friends', 'servers', 'channels',
        'blocked', 'status', 'pkey', 'server_key'
    )
    def __init__(
        self, reader, writer
        ):

        self.reader, self.writer = reader, writer

    async def clear_data(self):
        pass #plaseholder for decrypting data and parsing as json

    async def run_handler(self):
        while True:
            # try: header = int(await self.reader(users.HEADER_SIZE).decode())
            # except TypeError: continue
            data = await self.reader.read(1024)
            print(data.decode())
            self.writer.write(data)
            await self.writer.drain()