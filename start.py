from os import system

from app import app, loop, server_config
# pylint: disable=unused-wildcard-import
from routes import *  # noqa: F401 F403

system('cls')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 + 1

app.run(
    host=server_config['HOST'], port=server_config['PORT'],
    debug=server_config['debug'],
    loop=loop
)
