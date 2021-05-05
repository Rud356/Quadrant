import asyncio


from shutil import rmtree
from Quadrant.config import quadrant_config
from functools import wraps

loop = asyncio.get_event_loop()


def make_async_call(f):
    @wraps(f)
    def async_run(*args, **kwargs):
        return loop.run_until_complete(f(*args, **kwargs))
    return async_run


def clean_tests_folders():
    rmtree(quadrant_config.static_folder_location.value)
    rmtree(quadrant_config.media_folder_location.value)
