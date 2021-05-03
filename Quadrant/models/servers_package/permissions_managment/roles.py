from uuid import UUID

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, exc
from sqlalchemy.orm import relationship

from Quadrant.models.caching import FromCache
from Quadrant.models.db_init import Base
from .permissions import RolesPermissions

permissions_columns_names = {c.name for c in RolesPermissions.columns}


class ServerRole(Base):
    role_id = Column(BigInteger, primary_key=True)
    server_id = Column(ForeignKey("servers_package.id"))

    role_name = Column(String(length=50), nullable=False)
    role_position = Column(Integer, default=0)
    # TODO: replace placeholder for permissions
    color_code = Column(Integer, default=0xffffff)

    permissions = relationship(
        RolesPermissions, lazy='joined', cascade="all, delete-orphan", uselist=False
    )
    # Used to define cascade deletes when role is deleted
    _role_assignments = relationship("RolesToMember", lazy="noload", cascade="all, delete-orphan")
    _role_overwrites = relationship("RolesOverwrites", lazy="noload", cascade="all, delete-orphan")

    __tablename__ = "server_roles"

    @classmethod
    async def get_role(cls, server_id: UUID, role_id: int, *, session):
        try:
            return await session.query(ServerRole).options(FromCache("default")) \
                .filter(cls.server_id == server_id).get(role_id)

        except (OverflowError, exc.NoResultFound):
            raise ValueError("No such role")

    # TODO: make safe method with permission checking so participant doesn't edits higher roles
    async def _edit_role_permissions(self, *permissions_names_to_change: str, session) -> None:
        anything_changed = False
        for permission_id in permissions_names_to_change:
            if permission_id not in permissions_columns_names:
                continue

            anything_changed = True
            # Switching bool variables
            previous_value = getattr(self.permissions, permission_id)
            setattr(self.permissions, permission_id, not previous_value)

        if anything_changed:
            await session.commit()

        else:
            raise KeyError("Nothing been changed (invalid keys provided)")
