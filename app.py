import asyncio

from motor import motor_asyncio
from quart import Quart
from quart.json import JSONEncoder

from config import config
from bson import ObjectId
from datetime import datetime
from api_version import APIVersion


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
server_api_version = APIVersion.from_str(config['api_v'])


def conn_mongo(loop):
    client = motor_asyncio.AsyncIOMotorClient(config['mongo_conn_string'], io_loop=loop)

    if not config['debug']:
        db = client[config['database_name']]

    else:
        db = client['debug_chat']

    return db, client


loop = asyncio.get_event_loop()
db, client = conn_mongo(loop)