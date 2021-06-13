from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from pathvalidate import sanitize_filename
from sqlalchemy import Column, DateTime, ForeignKey, String, and_, select
from sqlalchemy.dialects.postgresql import UUID as db_UUID

from Quadrant.config import quadrant_config
from Quadrant.models.db_init import Base
from Quadrant.models.users_package import User


class UploadedFile(Base):
    file_id = Column(db_UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploader_id = Column(ForeignKey("users.id"), nullable=False)

    __tablename__ = "files"

    @classmethod
    async def create_file(cls, uploader: User, filename: str, *, session):
        """
        Creates record about upload on server.
        Note: this function does not creates a new directory or upload so you can change code however you would like.
        Set up any custom upload storage and drop it to it.

        :param uploader: user, who uploads upload.
        :param filename: filename.
        :param session: sqlalchemy session.
        :return: UploadedFile instance.
        """
        # TODO: add customization to uploads and filtering
        filename = sanitize_filename(filename)
        if len(filename) > 256:
            raise ValueError("Invalid upload name")

        new_file = cls(filename=filename, uploader_id=uploader.id)
        await session.commit()
        return new_file

    @classmethod
    async def get_file(cls, uploader_id, file_id: UUID, *, session) -> UploadedFile:
        """
        Gets exact upload from database
        (will be needed in admin api probably and is needed to check if attached upload exists).

        :param uploader_id: user id of someone, who uploads upload.
        :param file_id: id of upload which we want to find.
        :param session: sqlalchemy session.
        :return: UploadedFile instance.
        """
        query = select(cls).filter(
            and_(
                cls.uploader_id == uploader_id,
                cls.file_id == file_id
            )
        )
        result = await session.execute(query)

        return result.scalar_one()

    @property
    def filepath(self) -> Path:
        """Path to local upload"""
        return quadrant_config.uploads / self.file_id / self.filename

    def as_dict(self):
        return {
            "file_id": self.file_id,
            "filename": self.filename,
            "created_at": self.created_at
        }

