from __future__ import annotations

from hmac import compare_digest
from secrets import token_urlsafe

from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import backref, relationship

from .db_init import Base
from .user_model import User
from .utils import generate_internal_token
from .utils.hashing import hash_login, hash_password


class UserInternalAuthorization(Base):
    record_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False, unique=True, index=True)
    internal_token = Column(String(128), default=generate_internal_token, index=True, nullable=False)

    login = Column(String(64), nullable=True, unique=True, index=True)
    salt = Column(String(40), nullable=True)
    password = Column(String(64), nullable=True)

    user: User = relationship(
        User, uselist=False, backref=backref('internal_auth', cascade="all, delete-orphan"),
        lazy='joined'
    )

    __tablename__ = "users_auth"

    @staticmethod
    async def register_user_internally(
        username: str, login: str, password: str, *, session
    ) -> UserInternalAuthorization:
        login = hash_login(login)
        salt = token_urlsafe(30)
        # TODO: add way to run asynchronously
        password = hash_password(password, salt)

        user = User(username=username)
        user_auth = UserInternalAuthorization(login=login, password=password, salt=salt)

        session.add(user)
        user_auth.user.append(user)

        await session.commit()
        return user_auth

    @staticmethod
    async def authorize_with_token(token: str, *, session) -> UserInternalAuthorization:
        return await session.query(UserInternalAuthorization).join(User).filter(
            UserInternalAuthorization.internal_token == token,
            User.is_banned.is_(False)
        ).one()

    @staticmethod
    async def authorize(login: str, password: str, *, session) -> UserInternalAuthorization:
        login = hash_login(login)
        auth_user: UserInternalAuthorization = await session.query(UserInternalAuthorization).join(User).filter(
            User.is_banned.is_(False),
            UserInternalAuthorization.login == login,
        ).one()
        password = hash_password(password, auth_user.salt)

        if compare_digest(password, auth_user.password):
            return auth_user

        else:
            raise ValueError("Invalid password")


class OauthUserAuthorization(Base):
    record_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    oauth_provider = Column(String(100), nullable=True)
    oauth_token = Column(String(100), unique=True, index=True, nullable=True)
    refresh_token = Column(String(100), unique=True, index=True, nullable=True)

    user: User = relationship(
        UserInternalAuthorization, primaryjoin="UserInternalAuthorization.user_id == OauthUserAuthorization.user_id"
    )

# TODO: finish oauth later
