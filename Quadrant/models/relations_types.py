from enum import Enum


class UsersRelationType(Enum):
    none = 0
    blocked = 1
    friend_request_sender = 2
    friend_request_receiver = 3
    friends = 4
