import asyncio


from shutil import rmtree
from Quadrant.config import quadrant_config
from functools import wraps


def make_async_call(f):
    try:
        loop = asyncio.get_running_loop()

    except RuntimeError:
        loop = asyncio.get_event_loop()

    @wraps(f)
    def async_run(*args, **kwargs):
        return loop.run_until_complete(f(*args, **kwargs))
    return async_run


def create_test_folders():
    quadrant_config.profile_pictures_dir.mkdir(parents=True, exist_ok=True)
    quadrant_config.uploads.mkdir(parents=True, exist_ok=True)


def clean_tests_folders():
    rmtree(quadrant_config.media_folder_location.value, ignore_errors=True)
