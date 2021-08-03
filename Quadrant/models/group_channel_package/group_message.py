from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declared_attr

from Quadrant.models import users_package
from Quadrant.models.abstract.message import ABCMessage
from .exceptions import AuthorIsBannedException
from .group_ban import GroupBan

if TYPE_CHECKING:
    from .group_channels import GroupMessagesChannel


class GroupMessage(ABCMessage):
    __tablename__ = "group_messages"
    __mapper_args__ = {'polymorphic_identity': 'group_message', 'concrete': True}

    @declared_attr
    def channel_id(self):
        return Column(ForeignKey("group_channels.channel_id"), index=True, nullable=False)

    async def can_user_send_message_check(self, author: users_package.User, *, session):
        if await GroupBan.is_user_banned(self.id, author.id, session=session):
            raise AuthorIsBannedException("Author of message was banned from group")

    async def delete_by_channel_owner(
        self, delete_by: users_package.User, channel: GroupMessagesChannel, *, session
    ) -> GroupMessage.message_id:
        """
        Delete message in group by it's owner.

        :param delete_by: user, who requested message deletion.
        :param channel: group channel, which we want to delete.
        :param session: sqlalchemy session.
        :return: deleted message id.
        """
        deleted_message_id = self.id
        if delete_by.id == channel.owner_id:
            session.delete(self)
            await session.commit()
            return deleted_message_id

        else:
            raise PermissionError("User isn't a text channel owner so can not delete message")
