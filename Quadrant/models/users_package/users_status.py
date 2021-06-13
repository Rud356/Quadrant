from enum import Enum


class UsersStatus(Enum):
    offline = "offline"
    online = "online"
    away = "away"
    do_not_disturb = "do_not_disturb"
    asleep = "asleep"
