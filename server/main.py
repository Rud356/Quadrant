import os
import ssl
import asyncio
from modules.user import users

# -- constants -- #
HEADER_SIZE = 6
# -- constants -- #

def ssl_setup():
    # not working
    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    ssl_ctx.options |= ssl.OP_NO_TLSv1
    ssl_ctx.options |= ssl.OP_NO_TLSv1_1
    ssl_ctx.options |= ssl.OP_SINGLE_DH_USE
    ssl_ctx.options |= ssl.OP_SINGLE_ECDH_USE

    ssl_ctx.load_cert_chain(os.getcwd()+'/keys/server_cert.pem', keyfile=os.getcwd()+'/keys/server_key.pem')
    ssl_ctx.load_verify_locations(cafile='server_ca.pem')
    ssl_ctx.check_hostname = False
    ssl_ctx.set_ciphers('ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384')

    return ssl_ctx

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
    loop.create_task(await users.registrate_user(reader, writer, None))

async def server_make(host='127.0.0.1', port=12645):
    server = await asyncio.start_server(handle_conn, '127.0.0.1', port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(server_make())
    loop.run_forever()
