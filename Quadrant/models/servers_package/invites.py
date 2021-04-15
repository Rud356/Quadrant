from datetime import datetime, timedelta
from secrets import token_urlsafe

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, case, or_, select
from sqlalchemy.ext.hybrid import hybrid_property

from Quadrant.models import Base
from Quadrant.models.group_channel_package.invites import INVITE_CODE_BIT_LENGTH, invite_code_len


class ServerInvite(Base):
    invite_code = Column(
        String(invite_code_len), default=lambda: token_urlsafe(INVITE_CODE_BIT_LENGTH), primary_key=True
    )
    created_by_id = Column(ForeignKey("server_members.id"), nullable=False)
    server_id = Column(ForeignKey('servers_package.id'), nullable=False)

    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    users_limit = Column(Integer, default=10)
    users_used_invite = Column(Integer, default=0)

    __tablename__ = "server_invites"

    @hybrid_property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at or self.users_used_invite > self.users_used_invite

    @is_expired.expression
    def is_expired(cls):  # noqa
        return select(
            case(
                (or_(datetime.utcnow() > cls.expires_at, cls.users_used_invite > cls.users_used_invite), True),
                else_=False
            )
        )
