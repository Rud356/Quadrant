from inspect import getdoc
from dataclasses import dataclass

from app import app
from .bot_managment_routes import (
    change_nick, delete_bot, get_bots,
    registrating_bot, update_token
)
from .endpoints_routes import (
    create_dm, get_endpoint, get_endpoints, get_endpoints_dict,
    create_group, create_group_invite, get_invites, delete_invite,
    join_group, leave_group, kick_from_group
)
from .file_host import (
    get_file, get_profile_pic, upload_file,
    upload_profile_pic
)
from .messages_routes import (
    delete_message, edit_message, get_message,
    get_messages_after, get_messages_from,
    get_messages_latest, get_pinned_latest,
    get_pinned_messages_from, pin_message,
    send_message, unpin_message
)
from .relations_routes import (
    block_user, cancel_friend_request,
    delete_friend, get_blocked_users,
    get_incoming_requests, get_outgoing_requests,
    get_users_friends, response_friend_request,
    send_code_friend_request, send_friend_request,
    unblock_user
)
from .user_routes import (
    authorize_user, delete_user, keep_alive, logout_user, registrate_user,
    set_friend_code, set_nickname, set_status, set_text_status,
    update_users_token, user_from_id, user_about_self
)
from .ws_route import add_websocket


@dataclass
class Route:
    path: str
    function: callable
    methods: list = None


categories = {
    "Bot_managment": [
        Route("/api/bots", get_bots),
        Route("/api/bots/registrate", registrating_bot, ["POST"]),
        Route("/api/bots/<bot_id>/<nick>", change_nick, ["POST"]),
        Route("/api/bots/<bot_id>/update_token", update_token, ["POST"]),
        Route("/api/bots/<bot_id>", delete_bot, ["DELETE"]),
    ],
    "User_routes": [
        Route("/api/user/login", authorize_user, ["POST"]),
        Route("/api/user/logout", logout_user, ["POST", "GET", "DELETE"]),
        Route("/api/user/register", registrate_user, ["POST"]),
        Route("/api/user/<id>", user_from_id),
        Route("/api/user/me", user_about_self),
        Route("/api/user/me", delete_user, ["DELETE"]),
        Route("/api/user/keep-alive", keep_alive),
        Route("/api/user/update_token", update_users_token, ["POST"]),
        Route("/api/me/nick", set_nickname, ["POST"]),
        Route("/api/me/friend_code", set_friend_code, ["POST"]),
        Route("/api/me/status/<int:new_status>", set_status, ["POST"]),
        Route("/api/me/text_status", set_text_status, ["POST"]),
    ],
    "Relations_routes": [
        Route("/api/friends", get_users_friends),
        Route("/api/blocked", get_blocked_users),
        Route("/api/outgoing_requests", get_outgoing_requests),
        Route("/api/outgoing_requests/<id>", cancel_friend_request, ["DELETE"]),
        Route("/api/incoming_requests", get_incoming_requests),
        Route("/api/incoming_requests/<id>", response_friend_request, ["POST"]),
        Route("/api/friends/<id>", send_friend_request, ["POST"]),
        Route("/api/friends/request", send_code_friend_request, ["POST"]),
        Route("/api/friends/<id>", delete_friend, ["DELETE"]),
        Route("/api/blocked/<id>", block_user, ["POST"]),
        Route("/api/blocked/<id>", unblock_user, ["DELETE"])
    ],
    "Endpoint_routes": [
        Route("/api/endpoints", get_endpoints),
        Route("/api/endpoints/json", get_endpoints_dict),
        Route("/api/endpoints/<endpoint_id>", get_endpoint),
        Route("/api/endpoints/create_endpoint/dm", create_dm, ["POST"]),
        Route("/api/endpoints/create_endpoint/group/<title>", create_group, ["POST"]),
        Route("/api/endpoints/<group_id>/create_invite", create_group_invite, ["POST"]),
        Route("/api/endpoints/<group_id>/invites", get_invites),
        Route("/api/endpoints/<group_id>/invites", delete_invite, ["DELETE"]),
        Route("/api/endpoints/join", join_group, ["GET", "POST"]),
        Route("/api/endpoints/<group_id>/leave", leave_group, ["DELETE"]),
        Route("/api/endpoints/<group_id>/kick", kick_from_group, ["DELETE"]),
    ],
    "Message_routes": [
        Route("/api/endpoints/<endpoint_id>/messages", get_messages_latest),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>", get_message),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>/from", get_messages_from),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>/after", get_messages_after),
        Route("/api/endpoints/<endpoint_id>/messages/pinned", get_pinned_latest),
        Route("/api/endpoints/<endpoint_id>/messages/pinned/<message_id>/pinned/from", get_pinned_messages_from),
        Route("/api/endpoints/<endpoint_id>/messages", send_message, ["POST"]),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>", get_message),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>", delete_message, ["DELETE"]),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>", edit_message, ["PATCH"]),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>/pin", pin_message, ["PATCH"]),
        Route("/api/endpoints/<endpoint_id>/messages/<message_id>/unpin", unpin_message, ["PATCH"])
    ],
    "File_routes": [
        Route("/api/user/set_image", upload_profile_pic, ["POST"]),
        Route("/api/user/<user_id>/profile_pic", get_profile_pic),
        Route("/api/files/upload", upload_file, ["POST"]),
        Route("/api/files/<file_name>", get_file)
    ]
}


def init_routes():
    for category_routes in categories.values():
        for route in category_routes:
            # route: Route
            app.add_url_rule(
                route.path,
                view_func=route.function,
                methods=route.methods
            )

def generate_docs():
    with open("Docs.md", 'w') as d:
        d.writelines("# Routes\n\n")

        for k, category_routes in categories.items():
            d.writelines([f"## [{k}](docs/{k}.md)\n", "| route | method |\n", "| ----- | ------ |\n"])
            d.writelines([f"| {route.path} | {' '.join(route.methods) if route.methods else 'GET'} |\n" for route in category_routes])

            with open(f"docs/{k}.md", 'w') as doc:
                for route in category_routes:
                    doc.write(f"### Route: {route.path}\n")
                    doc.write(f"Methods: {' '.join(route.methods) if route.methods else 'GET'}\n")
                    doc.write(f"Description:\n{getdoc(route.function) or 'Yet to add'}\n\n")
