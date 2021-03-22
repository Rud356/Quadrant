from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Column, ForeignKey, String, DateTime, Boolean

from .db_init import Base


class AbstractMessage(Base):
    message_id = Column(BigInteger, primary_key=True)
    author_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pinned = Column(Boolean, default=False, nullable=False)
    edited = Column(Boolean, default=False, nullable=False)

    text = Column(String(2000), nullable=True)
    attached_file_id = Column(ForeignKey('files.id'), nullable=True)

    __abstract__ = True
