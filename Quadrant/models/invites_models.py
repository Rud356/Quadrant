from datetime import datetime, timedelta
from math import ceil
from secrets import token_urlsafe

from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, String, case, or_, select
from sqlalchemy.ext.hybrid import hybrid_property

from .db_init import Base

INVITE_CODE_BIT_LENGTH = 12
# Because token_urlsafe encodes bytes using base64, which splits bits sequence per 6 bits and encodes it as 8 bit chars,
# this is why we must take 8/6 ratio
invite_code_len = ceil(INVITE_CODE_BIT_LENGTH * (8 / 6))


class InvitesExceptions:
    class TooManyInvites(ValueError):
        ...

    class TooShortLifespan(ValueError):
        """Invite must live at least five minutes"""
        ...

    class InvalidUsersLimitValue(ValueError):
        ...


class GroupInvite(Base):
    invite_code = Column(
        String(invite_code_len), default=lambda: token_urlsafe(INVITE_CODE_BIT_LENGTH), primary_key=True
    )
    group_channel_id = Column(ForeignKey('group_channels'))

    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    users_limit = Column(SmallInteger, default=10)
    users_used_invite = Column(SmallInteger, default=0)

    __tablename__ = "group_invites"

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


class ServerInvite(Base):
    invite_code = Column(
        String(invite_code_len), default=lambda: token_urlsafe(INVITE_CODE_BIT_LENGTH), primary_key=True
    )
    server_id = Column(ForeignKey('servers.id'), nullable=False)

    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    users_limit = Column(SmallInteger, default=10)
    users_used_invite = Column(SmallInteger, default=0)

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
