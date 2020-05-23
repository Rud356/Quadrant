from enum import IntEnum


class ChannelType(IntEnum):
    dm = 0
    group = 1
    server_text = 2
    server_voice = 3
    server_category = 4

class Status(IntEnum):
    offline = 0
    online = 1
    asleep = 2
    away = 3
    dnd = 4
