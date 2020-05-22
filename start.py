from os import system
from app import app, loop, config
from routes import *


system('cls')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 + 1
print("Debug mode: ", config['debug'])
app.run(
    host=config['HOST'], port=config['PORT'],
    debug=config['debug'],
    loop=loop
)