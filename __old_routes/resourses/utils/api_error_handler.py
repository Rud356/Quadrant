from tornado.web import ErrorHandler
from __old_routes.resourses.utils import JsonHTTPError


class QuadrantAPIErrorHandler(ErrorHandler):
    async def prepare(self) -> None:
        raise JsonHTTPError(self._status_code)
