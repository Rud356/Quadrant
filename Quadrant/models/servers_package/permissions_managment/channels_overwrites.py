from __future__ import annotations

from typing import Optional, List
from uuid import UUID

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from Quadrant.models.caching import FromCache
from Quadrant.models.db_init import Base
from .permissions import RolesPermissionsOverwrites, UsersPermissionsOverwrites
from .roles import ServerRole


class RolesOverwrites(Base):
    overwrite_id = Column(BigInteger, primary_key=True)
    channel_id = Column(ForeignKey("server_channels.id"), nullable=False)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False)
    permissions_for_role_id = Column(ForeignKey('server_roles.id'), nullable=False)
    permissions_id = Column(ForeignKey("roles_overwritten_permissions.member_id"), nullable=False)

    permissions: RolesPermissionsOverwrites = relationship(
        RolesPermissionsOverwrites, lazy='joined', cascade="all, delete-orphan", uselist=False
    )
    __tablename__ = "roles_server_permissions_overwrites"

    @classmethod
    async def get_overwrites_by_role(
        cls, server_id: UUID, channel_id: int, role_id: int, *, session
    ) -> Optional[RolesOverwrites]:
        return await session.query(cls).filter(
            cls.server_id == server_id,
            cls.channel_id == channel_id,
            cls.permissions_for_role_id == role_id
        ).options(FromCache("default")).one_or_none()

    @classmethod
    async def get_permissions_overwrites_by_roles(
        cls, server_id: UUID, channel_id: int, roles_ids: List[int], *, session
    ) -> RolesOverwrites.permissions:
        return await session.query(cls.permissions).filter(
            cls.server_id == server_id,
            cls.channel_id == channel_id,
            cls.permissions_for_role_id.in_(roles_ids)
        ).options(FromCache("default")) \
            .join(ServerRole).order_by(ServerRole.role_position).one_or_none()


class UsersOverwrites(Base):
    overwrite_id = Column(BigInteger, primary_key=True)
    channel_id = Column(ForeignKey("server_channels.id"), nullable=False)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False)
    permissions_for_members_id = Column(ForeignKey('server_members.id'), nullable=False)

    permissions: UsersPermissionsOverwrites = relationship(
        UsersPermissionsOverwrites, lazy='joined', cascade="all, delete-orphan", uselist=False,
    )
    __tablename__ = "users_server_permissions_overwrites"

    @classmethod
    async def get_overwrites_for_channel(
            cls, server_id: UUID, channel_id: int, member_id: int, *, session
    ) -> Optional[UsersOverwrites]:
        return await session.query(cls).filter(
            cls.server_id == server_id,
            cls.channel_id == channel_id,
            cls.permissions_for_members_id == member_id
        ).options(FromCache("default")).one_or_none()
