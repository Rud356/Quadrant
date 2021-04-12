from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, func, not_, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID  # noqa
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import relationship

from Quadrant import models
from Quadrant.models.db_init import Base

INVITES_COUNT_LIMIT_PER_USER = 1000

ServerInvites = models.ServerInvite
InvitesExceptions = models.InvitesExceptions


class Server(Base):
    name = Column(String(50), nullable=False)
    owner_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    server_id = Column(db_UUID, primary_key=True, default=uuid4)

    bans = relationship("ServerBans", lazy="noload")
    members = relationship("ServerMembers", lazy="noload")
    invited = relationship("ServerInvite", lazy="noload")

    __tablename__ = "servers"

    @classmethod
    async def create_server(cls, owner: models.User, name: str, *, session):
        # TODO: validate server name
        new_server = cls(name=name, owner_id=owner)
        session.add(new_server)
        await session.commit()

        return new_server

    async def delete_server(self, delete_by: models.User, *, session) -> bool:
        if delete_by.id != self.owner_id:
            raise PermissionError("You can not delete the server!")

        session.delete(self)
        await session.commit()

        return True
