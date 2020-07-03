import asyncio
from os import mkdir

from motor import motor_asyncio
from quart import Quart

from json_encoder import CustomJSONEncoder

app = Quart(__name__)
app.json_encoder = CustomJSONEncoder
loop = asyncio.get_event_loop()
connected_users = {}

app.config["DEBUG"]: bool = True
app.config["ALLOW_REG"]: bool = True
app.config['UPLOAD_FOLDER']: str = "resourses/"
app.config["DB_CONN_STR"]: str = "mongodb://localhost:27017"
app.config["TTK"]: int = 10
app.config['MAX_CONTENT_LENGTH']: int = 20 * 1024 * 1024 + 1
app.config['LOGIN_CACHE_SIZE']: int = 1024


try:
    mkdir(app.config["UPLOAD_FOLDER"])

except FileExistsError:
    pass

client = motor_asyncio.AsyncIOMotorClient(
    app.config['DB_CONN_STR'],
    io_loop=loop
)

db = client["asyncio_chat"]
if app.config["DEBUG"]:
    db = client["debug_chat"]
