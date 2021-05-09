from typing import Awaitable, Optional

from tornado.web import ErrorHandler
from Quadrant.resourses.utils import JsonHTTPError


class QuadrantAPIErrorHandler(ErrorHandler):
    async def prepare(self) -> None:
        raise JsonHTTPError(self._status_code)
