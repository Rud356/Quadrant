from quart import Quart
from pymongo import MongoClient

app = Quart(__name__)
client = MongoClient('localhost', 27017)
