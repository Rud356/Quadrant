from functools import wraps
from typing import Awaitable, Callable, Optional

from tornado.web import RequestHandler

from __old_routes.resourses.utils import JsonHTTPError


def rest_authenticated(
    method: Callable[..., Optional[Awaitable[None]]]
) -> Callable[..., Optional[Awaitable[None]]]:
    @wraps(method)
    def wrapper(self: RequestHandler, *args, **kwargs):
        if not self.current_user:
            raise JsonHTTPError(403)

        return method(self, *args, **kwargs)
    return wrapper
