from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class FileUploadResponseSchema(BaseModel):
    file_id: UUID = Field(description="file id by which file resource should be found")
    filename: str = Field(description="file name, which also needed to get file")
    created_at: datetime = Field(description="when file was uploaded")


class UserProfilePictureUpdated(BaseModel):
    updated_image: bool = Field(default=True, description="Shows that there's a new image for user profile")
