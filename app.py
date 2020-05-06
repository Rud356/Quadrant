from quart import Quart

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = Quart(__name__)

engine = sqlalchemy.create_engine("sqlite:///data/discord_bot.sqlite")
Session = sessionmaker(engine)
session = Session()
Base = declarative_base()
