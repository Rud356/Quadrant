import sys, time
import json
import enum
import asyncio
if __name__ == "__main__":
    import database
else:
    import server_files.database

'''
File with reserved classes constructions that used just as sketchs
'''
Header = 8


class __Tools:
    @staticmethod
    def limint(num: int):
        return num.to_bytes(4, sys.byteorder)

class ResponceCodes(enum.Enum): pass

class messages:
    def __init__(
        self, author='system', content=None, attachments=None,
        endpoint: int=None
        ): pass

class server:
    pass

class ChannelTypes(enum.Enum):
    secret_dm = 0
    dm = 1
    chat = 2
    public = 3

class channels:
    def __init__(self): pass

class user:
    __slots__ = (
        'reader', 'writer', 'id',
        'nick', 'avatar', 'friends',
        'channels', 'blocked',
        'status', 'keys', 'run'
    )

    def __init__(self,
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
        keychain=None, auth=None):
        self.reader, self.writer = reader, writer
        self.keys = keychain
        self.run = False
        if auth is not None:
            self.run = True

            self.id = auth['id']
            self.nick = auth['nick']
            self.avatar = auth['avatar']
            # make them different ints before parsing
            self.channels = list(map(channels, auth['channels']))
            self.blocked = auth['blocked']


    def cleanify_data(self, data):
        # add loading via json and decrypting with keychain
        try: return data
        except: pass

    def encrypt_data(self, data):
        # yet another placeholder
        return data

    async def __send_back(self, data: (bytes or str)):
        self.writer.write(self.encrypt_data(data))
        await self.writer.drain()

    async def run_handler(self):
        while self.run:
            try: incoming_size = int(await self.reader(Header))
            except (TypeError, ValueError): continue
            data = await self.reader(incoming_size)
            #? parse msg