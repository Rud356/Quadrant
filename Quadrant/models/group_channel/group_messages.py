from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declared_attr

import Quadrant.models
from Quadrant import models
from Quadrant.models import DM_Message


class GroupMessage(DM_Message):
    __tablename__ = "group_messages"

    @declared_attr
    def channel_id(cls):  # noqa
        return Column(ForeignKey("group_channels.id"), index=True)

    async def delete_by_channel_owner(
        self, delete_by: models.User, channel: Quadrant.models.group_channel.group_channels.GroupMessagesChannel, *, session
    ) -> GroupMessage.message_id:
        msg_id = self.id
        if delete_by.id == channel.owner_id:
            session.delete(self)
            await session.commit()
            return msg_id

        else:
            raise PermissionError("User isn't a text_channel owner so can not delete message")