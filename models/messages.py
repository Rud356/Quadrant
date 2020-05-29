import json

from bson import ObjectId
from typing import List
from datetime import datetime
from dataclasses import dataclass

from functools import lru_cache
from app import db, CustomJSONEncoder

messages_db = db.messages


@dataclass
class Message:
    _id: ObjectId
    author: ObjectId
    endpoint: ObjectId

    content: str
    files: List[ObjectId]

    created_at: datetime

    pin: bool = False
    edited: bool = False

    @classmethod
    async def get_message(cls, message_id: ObjectId, endpoint_id: ObjectId):
        msg = await messages_db.find_one(
            {"$and": [
                {"_id": message_id},
                {"endpoint": endpoint_id}
            ]}
        )

        if not msg:
            raise ValueError("No such message")

        return cls(**msg)

    @classmethod
    async def get_messages_from(
        cls,
        from_message: ObjectId,
        endpoint_id: ObjectId
    ):
        msg_query = messages_db.find({"$and": [
            {"endpoint": endpoint_id},
            {"_id": {"$lt": from_message}}
            ]}
        ).sort("_id", -1).limit(100)
        messages = []

        async for message in msg_query:
            message = cls(**message)
            messages.append(message)

        return messages

    @classmethod
    async def get_messages_after(
        cls,
        after_message: ObjectId,
        endpoint_id: ObjectId
    ):
        msg_query = messages_db.find({"$and": [
            {"endpoint": endpoint_id},
            {"_id": {"$gt": after_message}}
            ]}
        ).sort("_id", -1).limit(100)
        messages = []

        async for message in msg_query:
            message = cls(**message)
            messages.append(message)

        return messages

    @classmethod
    async def send_message(
        cls, author: ObjectId, endpoint: ObjectId,
        content: str,
        files: List[ObjectId] = [],
    ):
        if len(content) > 3000:
            raise ValueError("Too long message")

        if not content and not files:
            raise ValueError("No content provided")

        new_message = {
            "author": author,
            "endpoint": endpoint,
            "content": content,
            "files": files,
            "created_at": datetime.utcnow(),
        }

        inserted = await messages_db.insert_one(new_message)
        new_message["_id"] = inserted.inserted_id

        return cls(**new_message)

    @staticmethod
    async def edit_message(
        author_id: ObjectId,
        message_id: str,
        new_content: str
    ):
        if len(new_content) > 3000:
            raise ValueError("Too long message")

        result = await messages_db.update_one(
            {"$and": [{"_id": message_id}, {"author": author_id}]},
            {"$set": {"content": new_content, "edited": True}}
        )
        return bool(result.modified_count)

    @classmethod
    async def batch_pinned(cls, from_message: ObjectId, endpoint_id: ObjectId):
        msg_query = messages_db.find({"$and": [
            {"endpoint": endpoint_id},
            {"_id": {"$lt": from_message}},
            {"pin": True}
            ]}
        ).sort("_id", -1).limit(100)
        messages = []

        async for message in msg_query:
            message = cls(**message)
            messages.append(message)

        return messages

    @staticmethod
    async def pin_message(from_endpoint: ObjectId, message_id: ObjectId):
        result = await messages_db.update_one(
            {
                "$and": [
                    {"_id": message_id},
                    {"endpoint": from_endpoint}
                ]
            }, {"$set": {"pin": True}}
        )
        return bool(result.modified_count)

    @staticmethod
    async def unpin_message(from_endpoint: ObjectId, message_id: ObjectId):
        result = await messages_db.update_one(
            {
                "$and": [
                    {"_id": message_id},
                    {"endpoint": from_endpoint}
                ]
            }, {"$set": {"pin": False}}
        )
        return bool(result.modified_count)

    @staticmethod
    async def delete_message(
        requester: ObjectId,
        message_id: ObjectId,
        endpoint_id: ObjectId
    ):
        result = await messages_db.delete_one(
            {"$and": [
                {"_id": message_id},
                {"author": requester},
                {"endpoint": endpoint_id}
            ]}
        )

        return bool(result.deleted_count)

    @staticmethod
    async def force_delete(message_id: ObjectId, endpoint_id: ObjectId):
        result = await messages_db.delete_one(
            {"$and": [
                {"_id": message_id},
                {"endpoint": endpoint_id}
            ]}
        )

        return bool(result.deleted_count)

    @lru_cache(10)
    def __str__(self):
        return json.dumps(
            self.__dict__,
            ensure_ascii=False,
            cls=CustomJSONEncoder
        )


class UpdateMessage:
    def __init__(self, updated_fields, upd_type):
        self.type = upd_type
        self.updated_fields = updated_fields
        self.cached = None

    def __str__(self):
        if self.cached is None:
            self.cached = json.dumps(
                {
                    "type": self.type,
                    "updated": self.updated_fields
                },
                ensure_ascii=False,
                cls=CustomJSONEncoder
            )

        return self.cached
