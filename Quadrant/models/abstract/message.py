from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, exc, select
from sqlalchemy.orm import declared_attr, relationship

from Quadrant.models import users_package
from Quadrant.models.db_init import Base
from Quadrant.models.general import UploadedFile

MESSAGES_PER_REQUEST = 100
# TODO: add messages reactions


class ABCMessage(Base):
    """
    Represents abstract message class that we inherit to create messages tables for other types of chats.
    """
    channel_id: Column
    message_id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pinned = Column(Boolean, default=False, nullable=False)
    edited = Column(Boolean, default=False, nullable=False)

    text = Column(String(2000), nullable=True)

    __abstract__ = True

    @declared_attr
    def channel_id(self):
        """
        Foreign key on table with channel id.
        """
        pass

    @declared_attr
    def author_id(self):
        """
        Foreign key on member of channel or server.
        """
        pass

    @declared_attr
    def attached_file_id(self):
        return Column(ForeignKey('files.file_id'), nullable=True)

    @declared_attr
    def attached_file(self):
        return relationship(UploadedFile, lazy="joined", uselist=False)

    async def user_can_send_message_check(self, author: users_package.User, *, session) -> None:
        """
        Checks if author can send a message to this channel.

        :param author: instance of User that we check permissions for.
        :param session: sqlalchemy session.
        :return: nothing (raises exception if doesn't have permissions).
        """
        pass

    @classmethod
    async def send_message(
        cls, channel, author: users_package.User, text: str, attached_file_id: Optional[UUID] = None,
        *, session
    ) -> ABCMessage:
        """
        Creates new message in text channel.

        :param channel: text channel instance.
        :param author: authors User model instance.
        :param text: message text that can be nothing (in case we have attached upload) and not longer than 2000 symbols.
        :param attached_file_id: attached upload instance.
        :param session: sqlalchemy session.
        :return: new message instance if everything is correct.
        """

        if not (await channel.is_member(channel.id, author, session=session)):
            raise cls.common_exc.UserIsNotAMemberException("You're not a member of chat")

        # Raises exception if this participant can send a message
        await cls.user_can_send_message_check(channel, author, session=session)

        if attached_file_id is None and len(text) == 0:
            raise ValueError("No content been posted")

        attached_file = None
        with suppress(exc.NoResultFound, ValueError):
            if attached_file_id is None:
                raise ValueError("UploadedFile isn't attached")

            attached_file = await UploadedFile.get_file(uploader=author, file_id=attached_file_id, session=session)

        if attached_file is None:
            new_message = cls(
                channel_id=channel.channel_id,
                author_id=author.id,
                text=text,
            )

        else:
            new_message = cls(
                channel_id=channel.channel_id,
                author_id=author.id,
                text=text,
                attached_file=attached_file
            )

        session.add(new_message)
        await session.commit()

        return new_message

    @classmethod
    async def get_message(cls, message_id: int, channel_id: UUID, *, session) -> ABCMessage:
        """
        Gives an message on channel with exact id.

        :param message_id: message id we want to get from channel.
        :param channel_id: channel id from which we request message.
        :param session: sqlalchemy session.
        :return: message (raises exception if didn't found any).
        """
        query = select(cls).filter(
            cls.channel_id == channel_id,
            message_id == message_id
        )
        query_result = await session.execute(query)
        return query_result.scalar_one()

    @classmethod
    async def get_last_message(
        cls, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Optional[ABCMessage]:
        """
        Gives latest message.

        :param channel_id: channel id from which we request message.
        :param select_pinned_only: flag that tells if we need to look up in pinned messages or not.
        :param session: sqlalchemy session.
        :return: message.
        """
        query = select(cls).filter(
            cls.channel_id == channel_id
        ).order_by(cls.message_id.desc())

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        query_result = await session.execute(query)
        return query_result.scalar_one_or_none()

    @classmethod
    async def get_messages_before(
        cls, message_id: int, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Tuple[ABCMessage]:
        """
        Gives messages that came before specified messages on timeline. This doesn't includes a message we look from.

        :param message_id: message id we want to start looking from.
        :param channel_id: channel id from which we request messages.
        :param select_pinned_only: flag that tells if we need to look up in pinned messages or not.
        :param session: sqlalchemy session.
        :return: messages that came before specified one.
        """
        query = select(cls).filter(
            cls.channel_id == channel_id, cls.message_id < message_id
        ).limit(MESSAGES_PER_REQUEST).order_by(cls.message_id.desc())

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        query_result = await session.execute(query)
        return query_result.scalars().all()

    @classmethod
    async def get_messages_after(
        cls, message_id: int, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> Tuple[ABCMessage]:
        """
        Gives messages that came after specified messages on timeline. This doesn't includes a message we look from.

        :param message_id: message id we want to start looking from.
        :param channel_id: channel id from which we request messages.
        :param select_pinned_only: flag that tells if we need to look up in pinned messages or not.
        :param session: sqlalchemy session.
        :return: messages that came after specified one.
        """
        query = select(cls).filter(
            cls.channel_id == channel_id,
            cls.message_id > message_id
        ).limit(MESSAGES_PER_REQUEST).order_by(cls.message_id.desc())

        if select_pinned_only:
            query = query.filter(cls.pinned.is_(True))

        query_result = await session.execute(query)
        return query_result.scalars().all()

    async def delete_message_by_author(self, delete_by: users_package.User, *, session) -> None:
        """
        Deletes message that been sent by exact participant.

        :param delete_by: the participant that asked to delete message.
        :param session: sqlalchemy session.
        :return: nothing (raises exceptions).
        """
        if self.author_id != delete_by.id:
            raise PermissionError("User tries to edit message even if he's not an author")

        session.delete(self)
        await session.commit()

    async def edit_message(self, new_text: str, edit_by: users_package.User, *, session) -> None:
        """
        Updates messages text (this can be executed only by author of message).

        :param new_text: text that will be set.
        :param edit_by: User instance that trying to edit message.
        :param session: sqlalchemy session.
        :return: nothing (raises exceptions).
        """
        if self.author_id != edit_by.id:
            raise PermissionError("User tries to edit message even if he's not an author")

        if len(self.text) == 0:
            raise ValueError("Invalid message length")

        # TODO: add more validations
        self.edited = True
        self.text = new_text
        await session.commit()

    async def pin_message(self, *, session) -> None:
        """
        Pins message.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        # Warning: permission check required
        if self.pinned:
            raise ValueError("Already pinned")

        self.pinned = True
        await session.commit()

    async def unpin_message(self, *, session) -> None:
        """
        Unpins message.

        :param session: sqlalchemy session.
        :return: nothing.
        """
        # Warning: permission check required
        if not self.pinned:
            raise ValueError("Message isn't pinned")

        self.pinned = False
        await session.commit()

    class common_exc:
        class UserIsNotAMemberException(PermissionError):
            """
            Exception that represents that participant isn't a channel member anymore.
            """
            pass
