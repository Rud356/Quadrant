from enum import Enum
from typing import Protocol
from uuid import UUID


class Status(Enum):
    online = "online"
    offline = "offline"
    away = "away"
    do_not_disturb = "do not disturb"
    asleep = "asleep"


class UserStatusRepo(Protocol):
    user_id: UUID
    status: Status

    async def set_status(self, new_status: Status) -> None:
        """
        Updates user's status that is displayed in his profile.

        :param new_status: new users status.
        :returns: nothing.
        """
