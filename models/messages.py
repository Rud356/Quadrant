from app import client

from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

db = client.messages


@dataclass
class Message:
    _id: ObjectId
    author: ObjectId
    endpoint: ObjectId
    content: str
    files: List[str]
    edited: bool = False
    pin: bool = False

    @classmethod
    def send_message(
        cls, author_id: str, endpoint: ObjectId, content: str,
        *files: List[str]
        ):
            if len(content) > 3000:
                raise ValueError("Too long message")

            #TODO: add checkups on files
            # likely raises bson.errors.InvalidId
            author_id = ObjectId(author_id)
            new_message = {
                "author": author_id,
                "endpoint": endpoint,
                "content": content,
                "files": files,
                "edited": False,
                "pin": False,
            }
            id = db.insert_one(new_message).inserted_id

            return cls(_id=id, **new_message)

    @staticmethod
    def edit_message(author_id: ObjectId, message_id: str, new_content: str):
        # we must make sure that our author is real and he does it
        # likely raises bson.errors.InvalidId
        message_id = ObjectId(message_id)

        if len(new_content) > 3000:
            raise ValueError("Too long message")

        result = db.update_one({"_id": message_id}, {"$set": [{"content": new_content}, {"edited": True}]})
        return bool(result.modified_count)

    @staticmethod
    def delete_message(author_id: ObjectId, message_id: str):
        # likely raises bson.errors.InvalidId
        message_id = ObjectId(message_id)

        result = db.delete_one({"$and": [{"_id": message_id}, {"author": author_id}]})
        return bool(result.deleted_count)

    @staticmethod
    def set_message_pin(author_id: ObjectId, message_id: str, pin: bool):
        # likely raises bson.errors.InvalidId
        message_id = ObjectId(message_id)

        result = db.update_one({"_id": message_id}, {"$set": [{"pin": pin}]})
        return bool(result.modified_count)