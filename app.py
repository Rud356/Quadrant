import asyncio
from quart import Quart
from motor import motor_asyncio
from quart.json import JSONEncoder
from bson import ObjectId
from app_config import server_config
from datetime import datetime


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()

            if isinstance(obj, ObjectId):
                return str(obj)

            iterable = iter(obj)
        except TypeError:
            pass

        else:
            return list(iterable)

        return JSONEncoder.default(self, obj)


app = Quart(__name__)
app.json_encoder = CustomJSONEncoder

loop = asyncio.get_event_loop()
app.config['UPLOAD_FOLDER'] = "resources/"
client = motor_asyncio.AsyncIOMotorClient(
    server_config['mongo_conn_string'],
    io_loop=loop
)

if not server_config['DEBUG']:
    db = client[server_config['database_name']]

else:
    db = client['debug_chat']
