import asyncio
from datetime import datetime
from os import mkdir

from bson import ObjectId
from motor import motor_asyncio
from quart import Quart
from quart.json import JSONEncoder
from quart_rate_limiter import RateLimiter

from app_config import server_config


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()

            if isinstance(obj, ObjectId):
                return str(obj)

            iterable = map(self.default, obj)
        except TypeError:
            pass

        else:
            return list(iterable)

        return JSONEncoder.default(self, obj)


app = Quart(__name__)

if not server_config['DEBUG']:
    rate_limiter = RateLimiter(app)

app.json_encoder = CustomJSONEncoder
loop = asyncio.get_event_loop()
app.config['UPLOAD_FOLDER'] = "resourses/"

try:
    mkdir(app.config['UPLOAD_FOLDER'])
except FileExistsError:
    pass

client = motor_asyncio.AsyncIOMotorClient(
    server_config['mongo_conn_string'],
    io_loop=loop
)

if not server_config['DEBUG']:
    db = client[server_config['database_name']]

else:
    db = client['debug_chat']

connected_users = {}
