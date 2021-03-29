import os
from hashlib import md5

from dogpile.cache.region import make_region

from Quadrant.models.db_init import Session
from . import caching_classes

# dogpile cache regions. A home base for cache configurations.
regions = {}

# scoped_session.

cache = caching_classes.ORMCache(regions)
cache.listen_on_session(Session)

# TODO: add settings to config and customize caching
root = "./dogpile_data/"

if not os.path.exists(root):
    os.makedirs(root)


def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash.

    """
    return md5(key.encode("ascii")).hexdigest()


# configure the "default" cache region.
regions["default"] = make_region(
    key_mangler=md5_key_mangler
).configure(
    "dogpile.cache.dbm",
    expiration_time=3600,
    arguments={"filename": os.path.join(root, "cache.dbm")},
)