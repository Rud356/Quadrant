from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, BigInteger, DateTime

from Quadrant import models
from Quadrant.models.db_init import Base


class RolesOverwrites(Base):
    overwrite_id = Column(BigInteger, primary_key=True)
    channel_id = Column(ForeignKey("server_channels.id"), nullable=False)
    server_id = Column(ForeignKey("servers.id"), nullable=False)
    permissions_for_role_id = Column(ForeignKey('server_roles.id'), nullable=False)

    # Placeholder for permissions int generation
    permissions = Column(BigInteger, default=0)
    __tablename__ = "roles_server_permissions_overwrites"


class UsersOverwrites(Base):
    overwrite_id = Column(BigInteger, primary_key=True)
    channel_id = Column(ForeignKey("server_channels.id"), nullable=False)
    server_id = Column(ForeignKey("servers.id"), nullable=False)
    permissions_for_members_id = Column(ForeignKey('server_members.id'), nullable=False)

    # Placeholder for permissions int generation
    permissions = Column(BigInteger, default=0)
    __tablename__ = "users_server_permissions_overwrites"
