from enum import Enum


# Fix for swagger docs
# See: https://github.com/tiangolo/fastapi/issues/329
class UsersStatus(str, Enum):
    offline = "offline"
    online = "online"
    away = "away"
    do_not_disturb = "do_not_disturb"
    asleep = "asleep"
