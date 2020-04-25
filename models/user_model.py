import random
from datetime import datetime

from app import db, session
from sqlalchemy import (
    Column,
    BigInteger, Text, VARCHAR,
    Boolean, DateTime,
    and_
)
from sqlalchemy.orm import Load, load_only, relationship

from .relations_model import RelationsModel, Relation
from .config_model import UserSettings, Setting
#TODO: make custom exceptions


class UserModel(db.Model):
    id: int = Column(BigInteger, primary_key=True)
    token: str = Column(VARCHAR(512), unique=True)
    login: str = Column(VARCHAR(512), unique=True, nullable=True)
    password: str = Column(VARCHAR(512), nullable=True)

    nick: str = Column(VARCHAR(50))
    bot: bool = Column(Boolean, default=False)
    belongs_to: int = Column(BigInteger, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)

    settings = relationship('UserSettings')

    __tablename__ = 'users'

    @staticmethod
    def _is_valid_user(user_id: int):
        user_count = session.query(UserModel).select()\
            .filter(UserModel.id == id).count()
        return bool(user_count)

    @staticmethod
    def _is_valid_token(token: str):
        unique_chars = set(token)
        allowed_chars = set('1234567890abcdef')
        return unique_chars == allowed_chars

    @staticmethod
    def _is_available_token(token: str):
        token_count = session.query(UserModel).select()\
            .filter(UserModel.token == token).count()

        return not bool(token_count)

    @classmethod
    def create_user(cls, nick: str, is_bot=False, **kwargs):
        if is_bot:
            allowed_keys = {'belongs_to',}
            required_keys = {'belongs_to',}
        else:
            allowed_keys = {'login', 'password'}
            required_keys = {'login', 'password'}

        kwargs = {k:v for k, v in kwargs if k in allowed_keys}

        for required in required_keys:
            if required not in kwargs:
                raise ValueError(f'No required key `{required}` found')

        #? for now keys are 256 chars length
        token = ''.join(random.choices('1234567890abcdef', k=256))

        while not cls._is_available_token(token):
            token = ''.join(random.choices('1234567890abcdef', k=256))

        new_user = cls(
            nick=nick, bot=is_bot,
            token=token,
            **kwargs
        )
        session.add(new_user)
        session.commit()

    @classmethod
    def get_user(cls, login='', password='', token=''):
        if not ((login and password) or token):
            raise ValueError('No auth data provided')
        elif token:
            user = cls.select().filter(
                cls.token == token
            ).first()

        elif login and password:
            user = cls.select().filter(
                and_(
                    cls.login == login,
                    cls.password == password
                )
            ).first()

        return user

    def send_pending(self, to_user: int):
        if not UserModel._is_valid_user(to_user):
            raise ValueError("Incorrect user id")

        RelationsModel.send_pending(self.id, to_user)

    def respond_pending(self, to_user: int, accept=True):
        if not UserModel._is_valid_user(to_user):
            raise ValueError("Incorrect user id")

        RelationsModel.respond_pending(self.id, to_user, accept)

    def delete_friend(self, unfriend: int):
        if not UserModel._is_valid_user(unfriend):
            raise ValueError("Incorrect user id")

        return RelationsModel.delete_friend(self.id, unfriend)

    @property
    def friends(self):
        users = RelationsModel._get_users_relationships(
            self.id, Relation.friends
        )
        return users

    @property
    def blocked(self):
        users = RelationsModel._get_users_relationships(
            self.id, Relation.blocked
        )
        return users

    @property
    def my_pendings(self):
        users = RelationsModel._get_users_relationships(
            self.id, Relation.pending
        )
        return users

    @property
    def pending_for_me(self):
        users = RelationsModel._get_related_like(
            self.id, Relation.pending
        )
        return users