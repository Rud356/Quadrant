from random import choices

from bson import ObjectId
from string import ascii_letters, digits
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

# my modules
from app import db
from .enums import ChannelType
from motor.motor_asyncio import AsyncIOMotorCollection

invites_db: AsyncIOMotorCollection = db.invites


def generate_code():
    char_set = ascii_letters + digits
    return choices(char_set, k=12)


@dataclass
class Invite:
    _id: ObjectId
    endpoint: ObjectId
    user_created: ObjectId
    expires_at: datetime

    code: str
    users_limit: int = -1
    users_passed: int = 0

    @staticmethod
    async def create_invite(endpoint: ObjectId, created_by: ObjectId, users_limit: int, expires_at: datetime):
        if not users_limit:
            raise ValueError("Can't make empty invite")

        code = generate_code()

        invite = {
            "endpoint": endpoint,
            "user_created": created_by,
            "users_limit": users_limit,
            "code": code,
            "users_passed": 0,
            "expires_at": expires_at,
        }
        await invites_db.insert_one(invite)
        return code

    @classmethod
    async def endpoints_invites(cls, endpoint_id: ObjectId):
        fine = []
        to_delete = []
        invites = invites_db.find({"endpoint": endpoint_id})

        async for invite in invites:
            invite = cls(**invite)
            if not invite.is_expired:
                fine.append()
            else:
                to_delete.append(invite._id)

        # auto-cleanup invites
        await invites_db.delete_many({"_id": {"$in": to_delete}})

        return fine

    @classmethod
    async def get_invite(cls, code: str):
        invite_obj = await invites_db.find_one({"code": code})
        if invite_obj:
            return cls(**invite_obj)

        raise ValueError("No such invite existing")

    @property
    def is_finite(self):
        return self.users_limit > 0

    @property
    def is_expired(self):
        if datetime.utcnow() < self.expires_at:
            if self.is_finite:
                if self.users_passed >= self.users_passed:
                    return True

        return False

    async def add_passed(self):
        await invites_db.update_one({"_id": self._id}, {"$inc": {"users_passed": 1}})
        self.users_passed += 1
