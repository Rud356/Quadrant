from app import client

from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorCollection

db: AsyncIOMotorCollection = client.messages


@dataclass
class Message:
    _id: ObjectId
    author: ObjectId
    endpoint: ObjectId

    content: str
    files: List[str]

    created_at: datetime

    pin: bool = False
    edited: bool = False

    @classmethod
    async def send_message(
        cls, author: ObjectId, endpoint: ObjectId, content: str,
        files: List[str]
    ):
        if len(content) > 3000:
            raise ValueError("Too long message")

        new_message = {
            "created_at": datetime.utcnow(),
            "author": author,
            "endpoint": endpoint,
            "content": content,
            "files": files,
        }

        id = await db.insert_one(new_message).inserted_id

        return cls(_id=id, **new_message)

    @staticmethod
    async def edit_message(author_id: ObjectId, message_id: str, new_content: str):
        # we must make sure that our author is real and he does it
        if len(new_content) > 3000:
            raise ValueError("Too long message")

        result = await db.update_one(
            {"$and": [{"_id": message_id}, {"author": author_id}]},
            {"$set": [{"content": new_content}, {"edited": True}]}
        )
        return bool(result.modified_count)

    @classmethod
    async def get_message(cls, message_id: ObjectId, from_channel: ObjectId):
        #! DONT FORGET TO VALIDATE THAT USER IS MEMBER OF CHANNEL
        msg = await db.find_one({"$and": [{"_id": message_id}, {"endpoint": from_channel}]})
        return cls(**msg)

    @classmethod
    async def get_messages(cls, from_message: ObjectId, from_channel: ObjectId) -> List[Message]:
        # messages from newest to oldest
        messages = []
        msg_query = db.find({"$and": [
            {"_id": from_message},
            {"endpoint": from_channel},
            {"_id": {"$lt": from_message}}
            ]}
        ).sort({"_id":-1}).limit(100)

        async for message in msg_query:
            message = cls(**message)
            messages.append(message)

        return messages

    @staticmethod
    async def set_message_pin(author_id: ObjectId, message_id: ObjectId, pin: bool):
        result = db.update_one({"_id": message_id}, {"$set": [{"pin": pin}]})
        return bool(result.modified_count)

    @staticmethod
    async def delete_message(author_id: ObjectId, message_id: ObjectId):
        result = await db.delete_one({"$and": [{"_id": message_id}, {"author": author_id}]})
        return bool(result.deleted_count)

    @staticmethod
    async def force_delete(message_id: ObjectId, channel_id: ObjectId):
        result = await db.delete_one({"$and": [{"_id": message_id}, {"endpoint": channel_id}]})
        return bool(result.deleted_count)