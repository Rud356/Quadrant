import asyncio
from functools import wraps

loop = asyncio.get_event_loop()


def make_async_call(f):
    @wraps
    def async_run(*args, **kwargs):
        loop.run_until_complete(f(*args, **kwargs))
    return async_run
