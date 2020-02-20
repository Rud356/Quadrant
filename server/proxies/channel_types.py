from enum import Enum

class ChannelTypes(Enum):
    pdm = 0
    dm = 1
    group_dm = 2
    channel = 3
    category_channel = 4
    voice_channel = 5