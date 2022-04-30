from typing import NamedTuple
from datetime import datetime
from uuid import UUID


class UserDTO(NamedTuple):
    """
    Data transfer object for user entity.
    """
    uid: UUID
    username: str
    discriminator: int
    registered_at: datetime
    status: str
    text_status: str
    is_banned: bool
