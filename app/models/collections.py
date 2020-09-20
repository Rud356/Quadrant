from pymongo import DESCENDING

from .mongo_conn import db

users_db = db.chat_users
messages_db = db.messages
invites_db = db.invites
files_db = db.files_db
endpoints_db = db.endpoints


async def make_index():
    await users_db.create_index([
        ("_id", DESCENDING),
        ("token", DESCENDING),
        ("login", DESCENDING),
        ("friend_code", DESCENDING)
    ], unique=True)
    await messages_db.create_index([
        ("_id", DESCENDING),
        ("author", DESCENDING),
        ("endpoint", DESCENDING),
        ("created_at", DESCENDING)
    ])
    await invites_db.create_index([
        ("_id", DESCENDING),
        ("endpoint", DESCENDING),
        ("code", DESCENDING),
        ("user_created", DESCENDING)
    ])
