from functools import partial

import rapidjson  # noqa: is in requirements
from rapidjson import DM_ISO8601, UM_CANONICAL  # noqa: is in requirements


class JsonWrapper:
    dumps = partial(rapidjson.dumps, ensure_ascii=False, uuid_mode=UM_CANONICAL, datetime_mode=DM_ISO8601)
    loads = partial(rapidjson.loads, uuid_mode=UM_CANONICAL, datetime_mode=DM_ISO8601)
