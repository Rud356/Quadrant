from dataclasses import dataclass
from datetime import datetime
from random import choices
from string import ascii_letters, digits

from bson import ObjectId

from app import db

invites_db = db.invites


def generate_code():
    char_set = ascii_letters + digits
    return choices(char_set, k=12)


@dataclass
class Invite:
    _id: ObjectId
    endpoint: ObjectId
    user_created: ObjectId
    expires_at: int

    code: str
    users_limit: int = -1
    users_passed: int = 0

    @staticmethod
    async def create_invite(
        endpoint: ObjectId,
        created_by: ObjectId,
        users_limit: int,
        expires_at: int
    ):
        if not users_limit:
            raise ValueError("Can't make empty invite")

        invites = await invites_db.count_documents({"endpoint": endpoint})

        if invites >= 25:
            raise Invite.TooManyInvites("Can't create more invites")

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

    @staticmethod
    async def delete_invite(code: str, endpoint: ObjectId):
        return await invites_db.delete_one({"code": code, "endpoint": endpoint})

    @classmethod
    async def endpoints_invites(cls, endpoint_id: ObjectId):
        fine = []
        to_delete = []
        invites = invites_db.find({"endpoint": endpoint_id})

        async for invite in invites:
            invite = cls(**invite)
            if not invite.is_expired:
                fine.append(invite)

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

    async def add_passed(self):
        await invites_db.update_one(
            {"_id": self._id},
            {"$inc": {"users_passed": 1}}
        )
        self.users_passed += 1

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

    class TooManyInvites(ValueError):
        ...