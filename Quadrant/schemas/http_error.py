from typing import List

from pydantic import BaseModel, Field


class HTTPErrorDetails(BaseModel):
    reason: str = Field(description="short text code of error")
    message: str = Field(description="message, describing what had gone wrong")


class HTTPError(BaseModel):
    details: HTTPErrorDetails = Field(description="details about error")
