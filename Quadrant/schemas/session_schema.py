from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from Quadrant.models.users_package.user_session import SESSIONS_PER_PAGE


class SessionSchema(BaseModel):
    session_id: int
    ip_address: str = Field(format="IPvAnyAddress")
    started_at: datetime
    is_alive: bool


class TerminatedSchema(BaseModel):
    session_id: int
    successfully_terminated: bool


class SessionPagesCountSchema(BaseModel):
    pages: int = Field(description="tells how many pages of sessions can be accessed")


class SessionsPageSchema(BaseModel):
    sessions: List[SessionSchema] = Field(max_length=SESSIONS_PER_PAGE)
