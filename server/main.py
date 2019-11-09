import asyncio
from modules import user

# -- constants -- #
HEADER_SIZE = 6
# -- constants -- #

async def handle_conn(reader, writer):
    # try:
        # pkg_size = int(await reader.read(HEADER_SIZE))
    # except TypeError:
        # writer.write(f'{3:<6}400') #invalid header
        # await writer.drain()
        # return
    #? some pre-authethication key sharing
    # pkey = await reader.read(pkg_size).decode() #placeholder yet
    # generate our key and send it
    # sample user object
    loop.create_task(user.users_s(reader, writer).run_handler())

async def server_make(host='127.0.0.1', port=12645):
    server = await asyncio.start_server(handle_conn, '127.0.0.1', port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(server_make())
    loop.run_forever()
