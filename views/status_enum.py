from enum import IntEnum


class Status(IntEnum):
    offline = 0
    online = 1
    asleep = 2
    away = 3
    dnd = 4
