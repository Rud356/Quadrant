from datetime import datetime

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, UniqueConstraint, DateTime, String, Boolean
from sqlalchemy.orm import relationship

from Quadrant.models.db_init import Base


class ServerMember(Base):
    member_id = Column(ForeignKey('users.id'), nullable=False)
    server_id = Column(ForeignKey("servers.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    nickname = Column(String(50), nullable=True)
    mute = Column(Boolean, default=False)
    deaf = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("server_id", "member_id", name="_unique_server_member"),
    )
    __tablename__ = "server_members"
