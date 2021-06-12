from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from Quadrant.models.users_package import UsersStatus


class UserRegistration(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    login: str = Field(min_length=8, regex=r"^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$")
    password: str = Field(
        min_length=8, max_length=128,
        regex=r"^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,128}$"
    )


class UserSchema(BaseModel):
    id: UUID
    color_id: int = Field(description="Color id that can be used to determine if user is the same")
    username: str = Field(min_length=1, max_length=50)
    status: UsersStatus = Field(description="users online/offline/etc. status")
    text_status: str = Field(description="custom users text status")
    registered_at: datetime = Field(description="when user was registered in ISO8601")
    is_bot: bool
    is_banned: bool
