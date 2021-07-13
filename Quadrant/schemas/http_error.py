from typing import Type, Optional, Union

from pydantic import BaseModel, Field


class HTTPErrorDetails(BaseModel):
    reason: str = Field(description="short text code of error")
    message: str = Field(description="message, describing what had gone wrong")


class HTTPError(BaseModel):
    details: HTTPErrorDetails = Field(description="details about error")


def http_error_example(reason: str, message: str, class_name: Optional[str] = None) -> Type[HTTPError]:
    class HTTPErrorWithExample(HTTPError):
        class Config:
            schema_extra = {
                "example": {
                    "reason": reason,
                    "message": message
                }
            }

    HTTPErrorWithExample.__name__ = class_name or f"HTTPError_{reason}"

    return HTTPErrorWithExample


UNAUTHORIZED_HTTPError = http_error_example("UNAUTHORIZED", "You aren't authorized to access this resource")
