from __future__ import annotations
from secrets import token_urlsafe
from hmac import compare_digest

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from .db_init import Base
from .registration_type import RegistrationType
from .user_model import User
from .utils import generate_internal_token
from .utils.hashing import hash_login, hash_password


class UserAuthorization(Base):
    record_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    internal_token = Column(String(128), default=generate_internal_token, index=True, nullable=False)

    oauth_token = Column(String(100), unique=True, index=True, nullable=True)
    refresh_token = Column(String(100), unique=True, index=True, nullable=True)

    login = Column(String(64), nullable=True, unique=True, index=True)
    password = Column(String(64), nullable=True)
    registration_type = Column(Enum(RegistrationType), nullable=False)

    user: User = relationship(User, uselist=False, cascade="all, delete-orphan")

    __tablename__ = "users_auth"

    @staticmethod
    async def register_user_internally(username: str, login: str, password: str, *, session) -> UserAuthorization:
        login = hash_login(login)
        salt = token_urlsafe(32)
        # TODO: add way to run asynchronously
        password = hash_password(password, salt)

        user = User(username=username)
        user_auth = UserAuthorization(login=login, password=password, registration_type=RegistrationType.internal)

        session.add(user)
        user_auth.user.append(user)

        await session.commit()
        return user_auth

    @staticmethod
    async def authorize_with_internal_token(token: str, *, session) -> UserAuthorization:
        return await session.query(UserAuthorization).join(User).filter(
            UserAuthorization.internal_token == token,
            User.is_banned.is_(False)
        ).one()

    @staticmethod
    async def authorize_with_login_and_password(login: str, password: str, *, session) -> UserAuthorization:
        login = hash_login(login)
        auth_user: UserAuthorization = await session.query(UserAuthorization).join(User).filter(
            User.is_banned.is_(False),
            UserAuthorization.login == login,
            UserAuthorization.registration_type.is_(RegistrationType.internal)
        ).one()
        password = hash_password(password, auth_user.salt)

        if compare_digest(password, auth_user.password):
            return auth_user

        else:
            raise ValueError("Invalid password")
