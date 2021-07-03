from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from Quadrant.models.users_package import UsersStatus


class UserAuthorization(BaseModel):
    # taken regex from: https://stackoverflow.com/questions/19605150
    login: str = Field(
        min_length=8, max_length=128,
        regex=r"^(?=.*[A-Za-z_\.])(?=.*\d)[A-Za-z_\.\d]{8,128}$",
        description=(
            "User login "
            "(requires at least one number and no special symbols; only english characters)"
        )
    )
    password: str = Field(
        min_length=8, max_length=128,
        regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&]{8,128}$",
        description=(
            "User password "
            "(Minimum eight characters, maximum 128 characters, at least one uppercase letter, "
            "one lowercase letter, one number and one special character)"
        )
    )

    class Config:
        schema_extra = {
            "example": {
                "login": "justSampleL0gin",
                "password": "XxRebel1243$xX",
            }
        }


class UserRegistration(UserAuthorization):
    username: str = Field(min_length=1, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "username": "Mememizing stuff",
                "login": "justSampleL0gin",
                "password": "XxRebel1243$xX",
            }
        }


class UserSchema(BaseModel):
    id: UUID
    color_id: int = Field(description="Color id that can be used to determine if user is the same")
    username: str = Field(min_length=1, max_length=50)
    status: UsersStatus = Field(description="users online/offline/etc. status")
    text_status: str = Field(max_length=256, description="custom users text status")
    registered_at: datetime = Field(description="when user was registered in ISO8601")
    is_bot: bool
    is_banned: bool


class SearchUserBody(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    color_id: int = Field(description="Color id that can be used to determine if user is the same")


class UserProfilePart(BaseModel):
    part_name: str = Field(description="Name of profile part")
    value: str = Field(description="Profile part value")
