from typing import Type
from abc import ABC, abstractmethod
from .user_profile import UserRepository
from .user_status import UserStatusRepo


class RepositoryFactory(ABC):
    user_repository: Type[UserRepository]
    user_status_repository: Type[UserStatusRepo]

    @abstractmethod
    async def get_user_repository(self, *args, **kwargs) -> UserRepository:
        """
        Prepares users repository for working.
        """
        pass

    @abstractmethod
    async def get_user_status_repository(
        self, *args, **kwargs
    ) -> UserStatusRepo:
        """
        Prepares users repository for working.
        """
        pass
