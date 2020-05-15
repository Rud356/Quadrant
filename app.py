from quart import Quart
from quart.json import JSONEncoder
from datetime import datetime
from motor import motor_asyncio
from api_version import APIVersion


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Quart(__name__)
app.json_encoder = CustomJSONEncoder
server_api_version = APIVersion.from_str("1.0.0b")

client = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client['chat_app']
