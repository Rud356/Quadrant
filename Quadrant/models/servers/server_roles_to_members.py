from sqlalchemy import BigInteger, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from Quadrant.models.db_init import Base
from .server_roles_model import ServerRole


class RolesToMember(Base):
    server_id = Column(ForeignKey("servers.id"), nullable=False)
    member_id = Column(ForeignKey("server_members.member_id"), nullable=False)
    role_id = Column(ForeignKey("server_roles.role_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("role_id", "member_id", name="_unique_server_members_role"),
    )
    __tablename__ = "server_members_roles"
