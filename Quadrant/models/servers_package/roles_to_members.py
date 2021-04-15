from sqlalchemy import BigInteger, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from Quadrant.models.db_init import Base
from .permissions_managment.roles import ServerRole


class RolesToMember(Base):
    role_assignment_id = Column(BigInteger, primary_key=True)
    role_id = Column(ForeignKey("server_roles.member_id"), nullable=False)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False)
    member_id = Column(ForeignKey("server_members.member_id"), nullable=False)

    role = relationship(ServerRole, lazy="joined", uselist=False)
    __table_args__ = (
        UniqueConstraint("member_id", "member_id", name="_unique_server_members_role"),
    )
    __tablename__ = "server_members_roles"
