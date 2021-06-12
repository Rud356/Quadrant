from functools import wraps

from sqlalchemy.exc import IntegrityError
from tornado.log import app_log

from __old_routes.resourses.utils import JsonHTTPError


def handle_integrity_error(f):
    @wraps(f)
    async def handler(self, *args, **kwargs):
        try:
            return await f(self, *args, **kwargs)

        except IntegrityError as err:
            await self.session.rollback()
            app_log.exception(err)
            raise JsonHTTPError(status_code=500, reason="Failed handling error")

    return handler
