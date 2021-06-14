from uuid import UUID

from Quadrant.models.users_package.relations_types import UsersRelationType
from pydantic import BaseModel, Field


class RelationWithUser(BaseModel):
    with_user_id: UUID = Field(description="User, with whom you've checked relations")
    status: UsersRelationType = Field(description="represents which relations you have with this user")
