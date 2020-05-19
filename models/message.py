from app import db

from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field
from motor.motor_asyncio import AsyncIOMotorCollection

messages_db: AsyncIOMotorCollection = db.messages


@dataclass
class Message:
    _id: ObjectId
    author: ObjectId
    endpoint: ObjectId

    content: str
    files: List[str]
    user_mentions: List[ObjectId]

    created_at: datetime

    pin: bool = False
    edited: bool = False

    @classmethod
    async def send_message(
        cls, author: ObjectId, endpoint: ObjectId, content: str,
        files: List[str] = [], user_mentions: List[ObjectId] = []
        ):
        if len(content) > 3000:
            raise ValueError("Too long message")

        new_message = {
            "created_at": datetime.utcnow(),
            "author": author,
            "endpoint": endpoint,
            "content": content,
            "files": files,
            "user_mentions": user_mentions
        }

        id = await messages_db.insert_one(new_message)
        new_message["_id"] = id.inserted_id
        return cls(**new_message)

    @staticmethod
    async def edit_message(author_id: ObjectId, message_id: str, new_content: str):
        # we must make sure that our author is real and he does it
        if len(new_content) > 3000:
            raise ValueError("Too long message")

        result = await messages_db.update_one(
            {"$and": [{"_id": message_id}, {"author": author_id}]},
            {"$set": {"content": new_content, "edited": True}}
        )
        return bool(result.modified_count)

    @classmethod
    async def get_message(cls, message_id: ObjectId, from_channel: ObjectId):
        #! DONT FORGET TO VALIDATE THAT USER IS MEMBER OF CHANNEL
        msg = await messages_db.find_one({"$and": [{"_id": message_id}, {"endpoint": from_channel}]})
        if not msg:
            raise ValueError("No such message")

        return cls(**msg)

    @classmethod
    async def get_messages(cls, from_message: ObjectId, from_channel: ObjectId):
        # messages from newest to oldest
        messages = []
        msg_query = messages_db.find({"$and": [
            {"endpoint": from_channel},
            {"_id": {"$lt": from_message}}
            ]}
        ).sort("_id", 1).limit(100)

        async for message in msg_query:
            message = cls(**message)
            messages.append(message)

        return messages

    @staticmethod
    async def set_message_pin(author_id: ObjectId, message_id: ObjectId, pin: bool):
        result = await messages_db.update_one({"_id": message_id}, {"$set": {"pin": pin}})
        return bool(result.modified_count)

    @staticmethod
    async def delete_message(author_id: ObjectId, message_id: ObjectId):
        result = await messages_db.delete_one({"$and": [{"_id": message_id}, {"author": author_id}]})
        return bool(result.deleted_count)

    @staticmethod
    async def force_delete(message_id: ObjectId, channel_id: ObjectId):
        result = await messages_db.delete_one({"$and": [{"_id": message_id}, {"endpoint": channel_id}]})
        return bool(result.deleted_count)