from datetime import datetime

from pydantic import BaseModel, Field


class SessionSchema(BaseModel):
    session_id: int
    ip_address: str = Field(format="IPvAnyAddress")
    started_at: datetime
    is_alive: bool


class TerminatedSchema(BaseModel):
    session_id: int
    successfully_terminated: bool
