from quart import Quart
from motor import motor_asyncio

app = Quart(__name__)
client = motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client['chat_app']
