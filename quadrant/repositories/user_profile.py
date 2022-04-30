from typing import Protocol
from uuid import UUID

from quadrant.dto import UserDTO


class UserRepository(Protocol):
    async def get_user_by_id(self, user_id: UUID) -> UserDTO:
        """
        Fetches user from database by his id.

        :param user_id: users id.
        :returns: User profile information DTO.
        :raises: UserProfileNotFound.
        """

    async def get_user_by_username_and_discriminator(
        self, username: str, discriminator: int
    ) -> UserDTO:
        """
        Fetches user from database by his username and discriminator.

        :param username: users name on server.
        :param discriminator: users additional id that assigned randomly.
        :returns: User profile information DTO.
        :raises: UserProfileNotFound.
        """

    async def update_text_status_for_user(
        self, user_id: UUID, new_text_status: str
    ) -> None:
        """
        Updates users text status.

        :param user_id: user whose text status we update.
        :param new_text_status: new text that will be set.
        :returns: nothing.
        :raises: UserProfileNotFound if there's no user with that id.
        """
