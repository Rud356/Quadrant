from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, select
from sqlalchemy.orm import declared_attr

from Quadrant.models import users_package
from Quadrant.models.caching import FromCache
from Quadrant.models.db_init import Base

MESSAGES_PER_REQUEST = 100
# TODO: add messages reactions


class ABCMessage(Base):
    channel_id: Column
    message_id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pinned = Column(Boolean, default=False, nullable=False)
    edited = Column(Boolean, default=False, nullable=False)

    text = Column(String(2000), nullable=True)
    # attached_file_id = Column(ForeignKey('files.id'), nullable=True)

    __abstract__ = True

    @declared_attr
    def channel_id(self):
        pass

    @declared_attr
    def author_id(self):
        pass

    async def user_can_send_message_check(self, author: users_package.User, *, session) -> None:
        pass

    @classmethod
    async def send_message(
        cls, channel, author: users_package.User, text: str, attached_file: Optional = None,
        *, session
    ) -> ABCMessage:

        if not (await channel.is_member(channel.id, author, session=session)):
            raise cls.common_exc.UserIsNotAMemberException("You're not a member of chat")

        # Raises exception if this user can send a message
        await cls.user_can_send_message_check(channel, author, session=session)

        if attached_file is None and len(text) == 0:
            raise ValueError("No content been posted")

        new_message = cls(
            channel_id=channel.channel_id,
            attached_file=attached_file,
            author_id=author.id,
            text=text,
        )

        session.add(new_message)
        await session.commit()

        return new_message

    @classmethod
    async def get_message(cls, message_id: int, channel_id: UUID, *, session) -> ABCMessage:
        query_result = await session.execute(
            select(cls).options(FromCache("default")).filter(
                cls.channel_id == channel_id, message_id == message_id
            )
        )

        return await query_result.one()

    @classmethod
    async def get_last_message(
        cls, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> ABCMessage:
        query = select(cls).filter(
            cls.channel_id == channel_id
        ).order_by(cls.message_id.desc())

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        query_result = await session.execute(query)
        return await query_result.one()

    @classmethod
    async def get_messages_before(
        cls, message_id: int, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Tuple[ABCMessage]:
        query = select(cls).filter(
            cls.channel_id == channel_id, cls.message_id < message_id
        ).limit(MESSAGES_PER_REQUEST)

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        query_result = await session.execute(query)
        return await query_result.all()

    @classmethod
    async def get_messages_after(
        cls, message_id: int, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Tuple[ABCMessage]:
        query = select(cls).filter(
            cls.channel_id == channel_id, cls.message_id > message_id
        ).limit(MESSAGES_PER_REQUEST)

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        query_result = await session.execute(query)
        return await query_result.all()

    async def delete_message_by_author(self, delete_by: users_package.User, *, session) -> None:
        if self.author_id != delete_by.id:
            raise PermissionError("User tries to edit message even if he's not an author")

        session.delete(self)
        await session.commit()

    async def edit_message(self, new_text: str, edit_by: users_package.User, *, session) -> None:
        if self.author_id != edit_by.id:
            raise PermissionError("User tries to edit message even if he's not an author")

        if len(self.text) == 0:
            raise ValueError("Invalid message length")

        # TODO: add more validations
        self.edited = True
        self.text = new_text
        await session.commit()

    async def pin_message(self, *, session) -> None:
        # Warning: permission check required
        if self.pinned:
            raise ValueError("Already pinned")

        self.pinned = True
        await session.commit()

    async def unpin_message(self, *, session) -> None:
        # Warning: permission check required
        if not self.pinned:
            raise ValueError("Message isn't pinned")

        self.pinned = False
        await session.commit()

    class common_exc:
        class UserIsNotAMemberException(PermissionError):
            pass
