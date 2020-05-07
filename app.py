from quart import Quart
from pymongo import MongoClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Quart(__name__)
client = MongoClient('localhost', 27017)
