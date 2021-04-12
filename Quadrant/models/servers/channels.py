from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, BigInteger, DateTime, Boolean
from sqlalchemy.orm import relationship

from Quadrant import models
from Quadrant.models.db_init import Base
from .permissions_managment.permissions import PermissionsSet, TextChannelPermissions


class ServerChannel(Base):
    channel_id = Column(BigInteger, primary_key=True)
    channel_name = Column(String(50), default="New channel")
    created_at = Column(DateTime, default=datetime.utcnow)

    server_id = Column(ForeignKey("servers.id"), nullable=False)
    category_id = Column(ForeignKey("server_categories_channels.id"))
    sync_overwrites_with_category = Column(Boolean, default=True)

    permissions: TextChannelPermissions = relationship(
        TextChannelPermissions, lazy='joined', cascade="all, delete-orphan", uselist=False
    )
    __tablename__ = "server_channels"
