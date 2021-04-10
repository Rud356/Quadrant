from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from Quadrant.models.db_init import Base
from .channels_overwrites import RolesOverwrites


class ServerRole(Base):
    role_id = Column(BigInteger, primary_key=True)
    role_position = Column(Integer, default=0)
    # Placeholder for generation of permissions int
    role_permissions = Column(BigInteger, default=0)
    color_code = Column(Integer, default=0xffffff)

    channel_id = Column(ForeignKey("servers_channels.id"))

    role_overwrites = relationship(RolesOverwrites, lazy="noload")

    __tablename__ = "server_roles"
