from os import system
from routes import *
from app import app, loop, config

system('cls')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 + 1

app.run(
    host=config['HOST'], port=config['PORT'],
    debug=config['debug'],
    loop=loop
)
