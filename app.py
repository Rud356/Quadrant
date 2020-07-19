import asyncio
from os import mkdir, environ

from motor import motor_asyncio
from quart import Quart

from utils import load_config
from json_encoder import CustomJSONEncoder

app = Quart(__name__)
app.json_encoder = CustomJSONEncoder
loop = asyncio.get_event_loop()
connected_users = {}
config = load_config()

app.config["DEBUG"]: bool = (
    environ.get('debug') in {"true", "1", "y", "yes", True} or
    config.getboolean("App", "debug") or
    False
)

app.config["ALLOW_REG"]: bool = (
    environ.get('allow_reg') in {"true", "1", "y", "yes", True} or
    config.getboolean("App", "allow_reg") or
    False
)
app.config['UPLOAD_FOLDER']: str = (
    environ.get("upload_folder") or
    config.get("App", "upload_folder")
)

app.config["DB_CONN_STR"]: str = (
    environ.get("db_conn_string") or
    config.get("App", "db_conn_string")
)

app.config["TTK"]: int = config.getint("App", "TTK") or 10

app.config['MAX_CONTENT_LENGTH']: int = config.getfloat(
    "App", "max_payload_size"
) * 1024 * 1024 + 1

if config.getfloat("App", "max_payload_size") == float("inf"):

    print("Do not set payload size as inf")
    print("Resetted value to default limit: 20MB")

    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024 + 1

app.config['LOGIN_CACHE_SIZE']: int = config.getint("App", "login_cache_size")

if app.config["TTK"] < 10:
    app.config["TTK"] = 10

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
