import asyncio
import random
HEADER_SIZE = 6
class client:
    def __init__(self, host='127.0.0.1', port=12645):
        self.host = host
        self.port = port

    async def run(self):
        reader, writer = await asyncio.open_connection(
            self.host, self.port
        )

async def tcp_echo_client(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 12645)
    msg = f'{len(message)}'.zfill(6) + message
    # message = (f'{3:<6}'+message).encode()
    # print(f'Send: {message!r}')
    writer.write(msg.encode())
    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
loop = asyncio.get_event_loop()

import json

login = json.dumps(
    {
    'login': 'hello',
    'pwd': 'world'
    }
)

asyncio.run(tcp_echo_client(login))