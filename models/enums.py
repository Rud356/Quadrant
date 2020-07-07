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


class UpdateType(IntEnum):
    # !THIS CODES WILL BE CHANGED SOON
    deleted_message = 0
    edited_message = 1
    pinned_message = 2
    unpinned_message = 3
    updated_nick = 4
    updated_status = 5
    updated_text_status = 6
    new_friend_request = 7
    new_friend = 8
    friend_request_rejected = 9
    friend_request_canceled = 10
    friend_deleted = 11
    got_blocked = 12
    image_updated = 13
    new_group_member = 14
    left_group_member = 15
    kicked_group_member = 16
    updated_user = 17
