import os
import asyncio

class server:
    def __init__(self, header = 4, max_content_len=2000):
        self.__HEADER = header
        self.__max_content_len = max_content_len

    async def handle_conn(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        pass

    async def run_server(self, host='127.0.0.1', port=12645):
        server = await asyncio.start_server(self.handle_conn, host, port)
        addr = server.sockets[0].getsockname()
        print(f"Server running on {addr}:{port}")

if __name__ == "__main__":
    # TODO: add arguments parsing over there or add config file
    loop = asyncio.get_event_loop()
    loop.create_task(server().run_server())
    loop.run_forever()