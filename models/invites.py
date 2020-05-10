from app import client
from random import choices
from string import ascii_letters, digits
from .enums import ChannelType

from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

db = client.invites


def generate_code():
    char_set = ascii_letters + digits
    return choices(char_set, k=12)



@dataclass
class Invite:
    _id: int
    endpoint: int
    code: str
    user_created: int
    users_limit: int = -1
    users_passed: int = 0
    expires_at: datetime

    @classmethod
    def create_invite(cls, endpoint: int, user_created: int, users_limit: int = -1, expires_at: datetime=None, **_):
        code = generate_code()
        new_invite = {
            "code": code,
            "endpoint": endpoint,
            "user_created": user_created,
            "users_limit": users_limit,
            "users_passed": 0,
            "expires_at": expires_at or datetime(2100, 12, 31)
        }
        id = db.insert_one(new_invite).inserted_id
        return cls(_id=id, **new_invite)

    @classmethod
    def endpoints_invites(cls, endpoint_id: int):
        invites = db.find({"endpoint": endpoint_id})
        invites = map(lambda invite: cls(**invite), invites)
        fine = list(filter(lambda invite: not invite.is_expired, invites))

        return fine

    @classmethod
    def get_invite(cls, code: str):
        invite_obj = db.find_one({"code": code})
        if invite_obj:
            return cls(**invite_obj)

        raise ValueError("No such invite existing")

    @property
    def is_expired(self):
        if datetime.utcnow() < self.expires_at:
            if self.is_finite:
                if self.users_passed >= self.users_passed:
                    return True

        return False

    @property
    def is_finite(self):
        return self.users_limit > 0

    def add_passed(self):
        db.update_one({"_id": self._id}, {"$inc": {"users_passed": 1}})