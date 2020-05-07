from enum import IntEnum


class ChannelType(IntEnum):
    dm = 0
    group = 1
    server_text = 2
    server_voice = 3
    server_category = 4
