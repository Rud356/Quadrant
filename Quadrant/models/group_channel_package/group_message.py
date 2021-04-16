from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declared_attr

from Quadrant.models import users_package
from Quadrant.models.dm_channel_package import DM_Message
from .group_ban import GroupBan
from .exceptions import AuthorIsBannedException

if TYPE_CHECKING:
    from .group_channels import GroupMessagesChannel


class GroupMessage(DM_Message):
    __tablename__ = "group_messages"

    @declared_attr
    def channel_id(cls):  # noqa
        return Column(ForeignKey("group_channels.id"), index=True)

    async def user_can_send_message_check(self, author: users_package.User, *, session):
        if await GroupBan.is_user_banned(self.id, author.id, session=session):
            raise AuthorIsBannedException("Author of message was banned from group")

    async def delete_by_channel_owner(
        self, delete_by: users_package.User, channel: GroupMessagesChannel, *, session
    ) -> GroupMessage.message_id:
        msg_id = self.id
        if delete_by.id == channel.owner_id:
            session.delete(self)
            await session.commit()
            return msg_id

        else:
            raise PermissionError("User isn't a text_channel owner so can not delete message")
