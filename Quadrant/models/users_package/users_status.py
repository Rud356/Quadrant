from enum import Enum


class UsersStatus(str, Enum):
    offline = 0
    online = 1
    away = 2
    do_not_disturb = 3
    asleep = 4
