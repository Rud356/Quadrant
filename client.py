import asyncio
import random
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
        print(f'Send: {message!r}')
        message = message
        await asyncio.sleep(random.randint(0, 10))
        writer.write(message.encode())
        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client('Hello World from person 1!'))