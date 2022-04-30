from uuid import UUID

from quadrant.repositories.user_status import (
    Status,
    UserStatusRepo
)


class UserStatus:
    user_id: UUID
    status: Status

    repository: UserStatusRepo

    def __init__(self, user_id: UUID, status: str, repository: UserStatusRepo):
        self.user_id = user_id
        self.status = Status[status]
        self.repository = repository

    async def set_status(self, new_status: Status) -> None:
        """
        Updates user's status that is displayed in his profile.

        :param new_status: new users status.
        :returns: nothing.
        """
        await self.set_status(new_status)
