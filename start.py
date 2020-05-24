from os import system
from app import app, loop, config

system('cls')
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 + 1
app.config['UPLOAD_FOLDER'] = "resources/"

app.run(
    host=config['HOST'], port=config['PORT'],
    debug=config['debug'],
    loop=loop
)
