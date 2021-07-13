from typing import Type, Optional

from pydantic import BaseModel, Field


class HTTPErrorDetails(BaseModel):
    reason: str = Field(description="short text code of error")
    message: str = Field(description="message, describing what had gone wrong")


class HTTPError(BaseModel):
    details: HTTPErrorDetails = Field(description="details about error")


errors = {}


def http_error_example(reason: str, message: str, class_name: Optional[str] = None) -> Type[HTTPError]:
    """
    This function constructs new class that will be used for showing example of errors response.

    :param reason: short text code of error.
    :param message: message, describing what had gone wrong.
    :param class_name: optional output class name.
    :return: new class, inherited from HTTPError.
    """
    class_name = class_name or f"{reason}_HTTPError"

    try:
        return errors[class_name]

    except KeyError:
        pass

    class Config:
        schema_extra = {
            "example": {
                "reason": reason,
                "message": message
            }
        }

    new_http_error = type(
        class_name,
        (HTTPError, ), {
            "Config": Config
        }
    )

    errors[class_name] = new_http_error

    return new_http_error  # noqa: this is inherited from HTTPError


UNAUTHORIZED_HTTPError = http_error_example("UNAUTHORIZED", "You aren't authorized to access this resource")
