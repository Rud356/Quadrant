import json
import enum
import modules.db as db

HEADER_SIZE = 6
clients = {}
db = db.sql_queries()

class responce_codes(enum.Enum):
    Logged_in = f"3".zfill(HEADER_SIZE) + "200"
    Login_fail = f"3".zfill(HEADER_SIZE) + "403"

class users:
    HEADER_SIZE = HEADER_SIZE
    __slots__ = (
        'reader', 'writer',
        'id', 'nick', 'avatar',
        'friends', 'channels',
        'blocked', 'status', 'keychain', 'run_loop'
    )

    def __init__(self, reader, writer, keychain=None, authorization_info=None):

        self.reader, self.writer = reader, writer
        self.keychain = keychain
        self.run_loop = False

        if authorization_info:
            print(authorization_info)
            self.run_loop = True
            self.id = authorization_info[0]
            self.nick = authorization_info[1]
            self.avatar = authorization_info[2]

            try: self.channels = list(map(int, authorization_info[3].split(', ')))
            except: self.channels = []

            try: self.blocked = list(map(int, authorization_info[4].split(', ')))
            except: self.blocked = []

            self.status = authorization_info[5]

            clients.update({self.id:self})

    async def __clear_data(self):
        pass #plaseholder for decrypting data and parsing as json

    async def __send_to_client(self, text):
        #! DO NOT USE TO SEND PACKAGES STRAIGHFORWARD USING IT
        self.writer.write(text)
        await self.writer.drain()

    async def send_system_MSG(self, responce_code): pass

    async def run_handler(self):
        while self.run_loop:
            try: header = int(await self.reader(users.HEADER_SIZE).decode())
            except (TypeError, ValueError): continue
            data = await self.reader(header)

        if not self.run_loop:
            self.writer.write(f'{3:<6}403'.encode())
            await self.writer.drain()

    @staticmethod
    def authorize(login_pkg):
        #SQL queries to db
        if 'login' and 'pwd' in login_pkg.keys():
            return db.authorize(
            login_pkg['login'],
            login_pkg['pwd']
        )
        else: return None

    @classmethod
    async def registrate_user(cls, reader, writer, keychain):
        tries = 0
        user = cls(reader, writer)
        while tries != 5:
            #? trying to read data
            try: header = int((await reader.read(users.HEADER_SIZE)).decode())
            except (TypeError, ValueError): continue

            data = str(await reader.read(header), 'utf-8')

            if data is not None:

                # loading login data
                try: login_pkg = json.loads(data)
                except: login_pkg = None

                if login_pkg is not None:
                    user_info = users.authorize(login_pkg)

                    #? logging in
                    if user_info is not None:
                        user = cls(reader, writer, keychain, user_info)
                        await user.__send_to_client(responce_codes.Logged_in.value.encode())
                        break

                #? telling user that password/login are incorrect
                    else: tries += 1; await user.run_handler()
                else: tries += 1; await user.run_handler()

        return user.run_handler()