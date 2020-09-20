import asyncio

from motor import motor_asyncio
import quart

from .config import BaseConfig
from .json_encoder import CustomJSONEncoder

loop = asyncio.get_event_loop()

app = quart.Quart(__name__)
app.config.from_object(BaseConfig)
app.json_encoder = CustomJSONEncoder

app.config.from_envvar("TEST")
app.config.from_envvar("DEBUG")
app.config.from_envvar("EXTERNAL_FILES_HOSTING")
app.config.from_envvar("MAX_CONTENT_LENGTH")

if app.config["MAX_CONTENT_LENGTH"] < 0:
    app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 + 1

mongo_client = motor_asyncio.AsyncIOMotorClient(
    app.config['MONGO_URI'],
    io_loop=loop
)

db = mongo_client["asyncio_chat"]

if app.config["TEST"]:
    db = mongo_client["debug_chat"]
