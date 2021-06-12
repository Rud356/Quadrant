from pydantic import BaseModel, Field


class HTTPError(BaseModel):
    reason: str = Field(description="short text code of error")
    message: str = Field(description="message, describing what had gone wrong")
