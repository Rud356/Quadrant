from __future__ import annotations

from datetime import datetime
from uuid import UUID

from .user_status import UserStatus
from quadrant.repositories import user_status, user_profile
from quadrant import dto


class UserProfile:
    uid: UUID
    username: str
    discriminator: int
    registered_at: datetime
    status: UserStatus
    text_status: str

    is_banned: bool
    repository: user_profile.UserRepository

    def __init__(
        self,
        uid: UUID,
        username: str,
        discriminator: int,
        registered_at: datetime,
        status: str,
        text_status: str,
        is_banned: bool,
        user_repository: user_profile.UserRepository,
        status_repository: user_status.UserStatusRepo
    ):
        self.uid = uid
        self.username = username
        self.discriminator = discriminator
        self.registered_at = registered_at
        self.status = UserStatus(uid, status, status_repository)
        self.text_status = text_status
        self.is_banned = is_banned

        self.repository = user_repository

    @classmethod
    async def get_user_by_id(
        cls, user_id: UUID,
        user_repository: user_profile.UserRepository,
        status_repository: user_status.UserStatusRepo
    ) -> UserProfile:
        """
        Fetches user from storage by users id.

        :param user_id: id of user we need to get.
        :param user_repository: instance of user repository that is used to
            fetch data.
        :param status_repository: repository for fetching users status.
        :returns: UserProfile instance.
        :raises: UserProfileNotFound.
        """
        user_data: dto.UserDTO = await user_repository.get_user_by_id(user_id)
        return cls(
            *user_data,
            user_repository=user_repository,
            status_repository=status_repository
        )

    @classmethod
    async def get_user_by_username_and_discriminator(
        cls, username: str, discriminator: int,
        user_repository: user_profile.UserRepository,
        status_repository: user_status.UserStatusRepo
    ) -> UserProfile:
        """
        Fetches user from storage by his username and discriminator.

        :param username: users name on server.
        :param discriminator: users additional id that assigned randomly.
        :param user_repository: instance of user repository that is used to
            fetch data.
        :param status_repository: repository for fetching users status.
        :returns: UserProfile instance.
        :raises: UserProfileNotFound.
        """
        user_data: dto.UserDTO = await user_repository.\
            get_user_by_username_and_discriminator(
                username, discriminator
            )

        return cls(
            *user_data,
            user_repository=user_repository,
            status_repository=status_repository
        )

    async def update_text_status(self, new_text_status: str) -> None:
        """
        Updates users text status.

        :param new_text_status: new text that will be set.
        :returns: nothing.
        """
        await self.repository.update_text_status_for_user(
            self.uid, new_text_status
        )
        self.text_status = new_text_status

    # TODO: add profile picture management
