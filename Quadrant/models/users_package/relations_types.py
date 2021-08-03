from enum import Enum


# Fix for swagger docs
# See: https://github.com/tiangolo/fastapi/issues/329
class UsersRelationType(str, Enum):
    none = "none"
    blocked = "blocked"
    friend_request_sender = "friend_request_sender"
    friend_request_receiver = "friend_request_receiver"
    friends = "friends"
