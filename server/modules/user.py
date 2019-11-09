import json
import modules.async_db
clients = {}

class users:
    HEADER_SIZE = 6
    __slots__ = (
        'reader', 'writer',
        'id', 'nick', 'avatar',
        'friends', 'servers', 'channels',
        'blocked', 'status', 'keychain', 'run_loop'
    )
    def __init__(self, reader, writer, keychain=None, authorization_info=None):

        self.reader, self.writer = reader, writer
        self.keychain = keychain
        self.run_loop = False
        if authorization_info:
            self.run_loop = True
            self.id = authorization_info[0]
            self.nick = authorization_info[1]
            self.avatar = authorization_info[2]
            self.servers = authorization_info[3]
            self.channels = authorization_info[4]
            self.blocked = authorization_info[5]
            self.status = authorization_info[6]
            clients.update({self.id:self})

    async def clear_data(self):
        pass #plaseholder for decrypting data and parsing as json

    async def run_handler(self):
        while self.run_loop:
            try: header = int(await self.reader(users.HEADER_SIZE).decode())
            except TypeError: continue
            data = await self.reader(header)
        if not self.run_loop:
            await self.writer(f'{3:<users.HEADER_SIZE}403'.encode())

    @staticmethod
    async def authorize(login, password):
        #SQL queries to db
        pass

    @classmethod
    async def registrate_user(cls, reader, writer, keychain):
        logged_in = False
        user = users(reader, writer)
        tries = 0
        while (not logged_in) or (tries == 5):
            try: header = int((await reader.read(users.HEADER_SIZE)).decode())
            except TypeError: continue
            data = str(await reader.read(header), 'utf-8')
            if data is not None:
                login, password = data.split(' -> ', 1)
                login_info = await users.authorize(login, password)
                if login_info:
                    user = cls(reader, writer, keychain, login_info)
                    logged_in = True
                    break
                else: tries += 1
        await user.run_handler()

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