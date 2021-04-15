from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, BigInteger, DateTime

from Quadrant import models
from Quadrant.models.db_init import Base


class Categories(Base):
    category_id = Column(BigInteger, primary_key=True)
    category_name = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False)

    __tablename__ = "server_categories"


class CategoriesChannels(Base):
    category_id = Column(ForeignKey("server_categories.id"), nullable=False)
    server_id = Column(ForeignKey("servers_package.id"), nullable=False)
    channel_id = Column(ForeignKey("server_channels.id"), nullable=False)

    __tablename__ = "server_categories_channels"
