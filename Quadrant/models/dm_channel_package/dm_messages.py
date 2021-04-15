from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, select
from sqlalchemy.orm import declared_attr

from Quadrant.models import users_package
from Quadrant.models.db_init import Base
from Quadrant.models.caching import FromCache
from .exceptions import UserIsNotAMemberException, BlockedByOtherParticipantException

if TYPE_CHECKING:
    from .dm_channels import DirectMessagesChannel

MESSAGES_PER_REQUEST = 100
# TODO: add messages reactions


class DM_Message(Base):
    message_id = Column(BigInteger, primary_key=True)
    author_id = Column(ForeignKey('users_package.id'), nullable=False)
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
        cls, channel: DirectMessagesChannel, author: users_package.User, text: str, attached_file: Optional = None,
        *, session
    ) -> DM_Message:
        if not (await channel.is_member(channel.id, author, session=session)):
            raise UserIsNotAMemberException("You're not a member of chat")

        if users_package.UsersRelations.get_relationships_status_with(
            author.id, await channel.other_participant(author), session=session
        ) == users_package.UsersRelationType.blocked:
            raise BlockedByOtherParticipantException("User has been blocked by other participant")

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
    async def get_message(cls, message_id: int, channel_id: UUID, *, session) -> DM_Message:
        query_result = await session.execute(
            select(cls).options(FromCache("default")).filter(
                cls.channel_id == channel_id, message_id == message_id
            )
        )

        return await query_result.one()

    @classmethod
    async def get_last_message(
        cls, channel_id: UUID, select_pinned_only: bool = False, *, session
    ) -> DM_Message:
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
    ) -> Tuple[DM_Message]:
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
    ) -> Tuple[DM_Message]:
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
