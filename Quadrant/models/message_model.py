from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import declared_attr

from Quadrant import models
from .db_init import Base

MESSAGES_PER_REQUEST = 100
# TODO: add messages reactions


class DM_Message(Base):
    message_id = Column(BigInteger, primary_key=True)
    author_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pinned = Column(Boolean, default=False, nullable=False)
    edited = Column(Boolean, default=False, nullable=False)

    text = Column(String(2000), nullable=True)
    attached_file_id = Column(ForeignKey('files.id'), nullable=True)

    __tablename__ = "dm_messages"

    @declared_attr
    def channel_id(cls):  # noqa
        return Column(ForeignKey("dm_channels.id"), index=True)

    @classmethod
    async def send_message(
        cls, channel: models.DirectMessagesChannel, author: models.User, text: str, attached_file: Optional = None,
        *, session
    ) -> models.DM_Message:
        if not (await channel.is_member(author, session=session)):
            raise PermissionError("You're not a member of chat")

        if attached_file is None and len(text) == 0:
            raise ValueError("No content been posted")

        new_message = cls(
            channel_id=channel.channel_id, author_id=author.id,
            text=text, attached_file=attached_file
        )

        session.add(new_message)
        await session.commit()

        return new_message

    @classmethod
    async def get_message(cls, message_id: int, channel_id: UUID, *, session) -> models.DM_Message:
        return await session.query(cls).filter(
            cls.channel_id == channel_id, message_id == message_id
        ).one()

    @classmethod
    async def get_last_message(
        cls, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> models.DM_Message:
        query = session.query(cls).filter(
            cls.channel_id == channel_id
        ).order_by(cls.message_id.desc())

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        return await query.one()

    @classmethod
    async def get_messages_before(
        cls, message_id: int, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Tuple[models.DM_Message]:
        query = session.query(cls).filter(
            cls.channel_id == channel_id, cls.message_id < message_id
        ).limit(MESSAGES_PER_REQUEST)

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        return await query.all()

    @classmethod
    async def get_messages_after(
        cls, message_id: int, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Tuple[models.DM_Message]:
        query = session.query(cls).filter(
            cls.channel_id == channel_id, cls.message_id > message_id
        ).limit(MESSAGES_PER_REQUEST)

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        return await query.all()

    async def delete_message_by_author(self, delete_by: models.User, *, session) -> None:
        if self.author_id != delete_by.id:
            raise PermissionError("User tries to edit message even if he's not an author")

        session.delete(self)
        await session.commit()

    async def edit_message(self, new_text: str, edit_by: models.User, *, session) -> None:
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


class GroupMessage(DM_Message):
    __tablename__ = "group_messages"

    @declared_attr
    def channel_id(cls):  # noqa
        return Column(ForeignKey("group_channels.id"), index=True)

    async def delete_by_channel_owner(
        self, delete_by: models.User, channel: models.GroupMessagesChannel, *, session
    ) -> GroupMessage.message_id:
        msg_id = self.id
        if delete_by.id == channel.owner_id:
            session.delete(self)
            await session.commit()
            return msg_id

        else:
            raise PermissionError("User isn't a channel owner so can not delete message")
