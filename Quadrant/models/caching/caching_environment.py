from hashlib import md5
from copy import copy

from dogpile.cache.region import make_region

from Quadrant.config import quadrant_config
from Quadrant.models.db_init import Session
from . import caching_classes

regions = {}

cache = caching_classes.ORMCache(regions)
cache.listen_on_session(Session)


def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash.

    """
    return md5(key.encode("ascii")).hexdigest()


# TODO: Add more configuring
# TODO: Use more regions for caching
if quadrant_config.DBCachingConfig.enable_caching.value:
    regions["default"] = make_region(
        key_mangler=md5_key_mangler
    ).configure(
        quadrant_config.DBCachingConfig.caching_backend.value,
        expiration_time=quadrant_config.DBCachingConfig.cache_expiration_time.value,
        arguments=quadrant_config.DBCachingConfig.arguments.value,
    )

    regions["dm_channels"] = make_region(
        key_mangler=md5_key_mangler
    ).configure(
        quadrant_config.DBCachingConfig.caching_backend.value,
        expiration_time=quadrant_config.DBCachingConfig.cache_expiration_time.value,
        arguments=quadrant_config.DBCachingConfig.arguments.value,
    )

else:
    regions["default"] = make_region(key_mangler=md5_key_mangler).configure("dogpile.cache.null")
    regions["dm_channels"] = copy(regions["default"])
