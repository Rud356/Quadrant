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

    for i in range(0, 15):
        # message = (f'{3:<6}'+message).encode()
        # print(f'Send: {message!r}')
        await asyncio.sleep(random.randint(0, 3))
        writer.write(b'3     Hi!')
        if i//5 == 0:
            data = await reader.read(100)
            print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
loop = asyncio.get_event_loop()
asyncio.run(tcp_echo_client('Hi!'))