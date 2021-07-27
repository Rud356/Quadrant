from __future__ import annotations

from uuid import UUID
from typing import Optional
from hmac import compare_digest
from secrets import token_urlsafe

from sqlalchemy import BigInteger, Column, ForeignKey, String, select
from sqlalchemy.orm import backref, relationship, Mapped

from Quadrant.models.db_init import Base, AsyncSession
from Quadrant.models.utils import generate_internal_token
from Quadrant.models.utils.hashing import hash_login, hash_password
from Quadrant.quadrant_logging import gen_log
from .user import User, UsersCommonSettings


class UserInternalAuthorization(Base):
    user_id: Mapped[UUID] = Column(ForeignKey('users.id'), nullable=False, unique=True, index=True)
    internal_token: Mapped[str] = Column(String(128), primary_key=True)

    login: Mapped[Optional[str]] = Column(String(64), nullable=True, unique=True, index=True)
    password: Mapped[Optional[str]] = Column(String(64), nullable=True)
    salt: Mapped[Optional[str]] = Column(String(40), nullable=True)

    user: User = relationship(
        User, uselist=False, backref=backref('internal_auth', cascade="all, delete-orphan"),
        lazy='joined'
    )

    __tablename__ = "users_auth"

    # TODO: add fetching Oauth authorization records
    # TODO: add TOTP

    @staticmethod
    async def register_user_internally(
        username: str, login: str, password: str, *, session: AsyncSession
    ) -> UserInternalAuthorization:
        """
        Creates internal user account.

        :param username: username.
        :param login: users login.
        :param password: users password.
        :param session: sqlalchemy session.
        :return: UserInternalAuthorization instance.
        """
        login = hash_login(login)
        salt = token_urlsafe(30)
        # TODO: fix slow hashing if executor is used
        # Somehow without async loops it runs way faster than with
        # When was ran locally through ProcessPoolExecutor 3 users were created in 4 seconds
        # while in sync mode just 300ms
        password = hash_password(password, salt)
        internal_token = generate_internal_token()
        user = User(username=username, users_common_settings=UsersCommonSettings())
        user_auth = UserInternalAuthorization(
            login=login, password=password, internal_token=internal_token,
            salt=salt, user=user
        )

        session.add(user_auth)
        await session.commit()
        user.profile_picture_path.mkdir()
        gen_log.debug(f"New user created with id -> {user_auth.user_id}")
        return user_auth

    @classmethod
    async def authorize_with_token(
        cls, token: str, is_bot: bool, *, session: AsyncSession
    ) -> UserInternalAuthorization:
        """
        Authorizes user using provided token.

        :param token: user token.
        :param is_bot: represents if we must look for bots or normal users.
        :param session: sqlalchemy session.
        :return: UserInternalAuthorization instance.
        """
        query = select(UserInternalAuthorization) \
            .join(User).filter(
                UserInternalAuthorization.internal_token == token,
                User.is_banned.is_(False),
                User.is_bot.is_(is_bot)
            )
        query_result = await session.execute(query)
        auth_user: UserInternalAuthorization = query_result.scalar_one()
        gen_log.debug(f"User with id {auth_user.user_id} is authorized by token")
        return auth_user

    @classmethod
    async def authorize(cls, login: str, password: str, *, session: AsyncSession) -> UserInternalAuthorization:
        """
        Authorizes user with login and password.

        :param login: user login.
        :param password: user password.
        :param session: sqlalchemy session.
        :return: UserInternalAuthorization instance.
        """
        login = hash_login(login)
        query = select(cls).join(User).filter(
            User.is_banned.is_(False),
            UserInternalAuthorization.login == login,
        )
        query_result = await session.execute(query)
        auth_user: UserInternalAuthorization = query_result.scalar_one()
        password = hash_password(password, auth_user.salt)  # noqa: this will be a string

        if compare_digest(password, auth_user.password):
            return auth_user

        else:
            raise ValueError(f"Invalid password for user")

    async def delete_account(self, *, session) -> bool:
        """Deletes user account."""
        session.delete(self)
        await session.commit()

        return True


class OauthUserAuthorization(Base):
    record_id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    oauth_provider = Column(String(100), nullable=True)
    oauth_token = Column(String(100), unique=True, index=True, nullable=True)
    refresh_token = Column(String(100), unique=True, index=True, nullable=True)

    user: User = relationship(
        UserInternalAuthorization,
        primaryjoin="UserInternalAuthorization.user_id == OauthUserAuthorization.user_id",
        lazy='joined'
    )
    __abstract__ = True

# TODO: finish oauth later
