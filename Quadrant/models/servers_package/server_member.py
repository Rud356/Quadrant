from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime,
    ForeignKey, String, PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship

from Quadrant import models
from Quadrant.models.db_init import Base
from .permissions_managment.roles import ServerRole
from .roles_to_members import RolesToMember

MAX_ROLES_PER_USER = 100


class ServerMember(Base):
    member_id = Column(ForeignKey('users_package.id'), nullable=False)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    nickname = Column(String(50), nullable=True)
    mute = Column(Boolean, default=False)
    deaf = Column(Boolean, default=False)

    roles_assignments = relationship(
        RolesToMember, lazy="joined", primaryjoin="""and_(
            RolesToMember.member_id == ServerMember.member_id,
            RolesToMember.server_id == ServerMember.server_id
        )
        """, cascade="all, delete-orphan", order_by="RolesToMember.role_position.desc()"
    )

    _created_by_member_invites = relationship(
        "ServerInvite", lazy="noload",
        primaryjoin="""and_(
            ServerMember.member_id == ServerInvite.created_by_id,
            ServerMember.server_id == ServerInvite.server_id
        )
        """, cascade="all, delete-orphan"
    )
    __table_args__ = (
        PrimaryKeyConstraint("server_id", "member_id", name="_unique_server_member"),
    )
    __tablename__ = "server_members"

    async def assign_role(self, assigned_by: models.User, role: ServerRole, *, session) -> RolesToMember:
        # TODO: check permissions to assign roles

        new_role = RolesToMember(server_id=self.server_id, member_id=self.id, role=role)
        await session.commit()
        return new_role

