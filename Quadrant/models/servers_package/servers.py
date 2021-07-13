from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, ForeignKey, String, func, not_, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship
from sequential_uuids.generators import uuid_time_nextval

import Quadrant.models.servers_package.server_invite
from Quadrant import models
from Quadrant.models.db_init import Base
from .server_member import ServerMember
from .server_ban import ServerBan
from .server_invite import ServerInvite

INVITES_COUNT_LIMIT_PER_USER = 1000


class Server(Base):
    name = Column(String(50), nullable=False)
    owner_id = Column(ForeignKey('users_package.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    server_id = Column(db_UUID(as_uuid=True), primary_key=True, default=uuid_time_nextval)

    _bans = relationship(ServerBan, lazy="noload", cascade="all, delete-orphan")
    _members = relationship(ServerMember, lazy="noload", cascade="all, delete-orphan")
    _invites = relationship(ServerInvite, lazy="noload", cascade="all, delete-orphan")

    __tablename__ = "servers_package"

    @classmethod
    async def create_server(cls, owner: models.User, name: str, *, session):
        # TODO: validate server name
        new_server = cls(name=name, owner_id=owner)
        session.add(new_server)
        await session.commit()

        return new_server

    @staticmethod
    async def is_member(server_id: UUID, user: models.User, *, session):
        return await session.query(
            session.query(Server).filter(
                ServerMember.member_id == user.id,
                Server.server_id == server_id
            ).exists()
        ).scalar() or False

    async def update_name(self, new_name: str, update_by: models.User, *, session) -> None:
        # TODO: validate name
        # TODO: check permissions
        self.name = new_name
        await session.commit()

    async def transfer_ownership(self, from_user: models.User, to_user: models.User, *, session) -> None:
        if not (await self.is_member(self.id, to_user, session=session)):
            raise ValueError("User is not a member of this server")

        if self.owner_id != from_user.id:
            raise PermissionError("User can not transfer ownership because he's not an owner")

        self.owner_id = to_user.id
        await session.commit()

    async def delete_server(self, delete_by: models.User, *, session) -> bool:
        if delete_by.id != self.owner_id:
            raise PermissionError("You can not delete the server!")

        session.delete(self)
        await session.commit()

        return True
