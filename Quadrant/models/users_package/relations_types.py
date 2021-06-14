from enum import Enum


class UsersRelationType(Enum):
    none = "none"
    blocked = "blocked"
    friend_request_sender = "friend_request_sender"
    friend_request_receiver = "friend_request_receiver"
    friends = "friends"
