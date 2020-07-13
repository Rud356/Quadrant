from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app
from models.enums import UpdateType
from models.message_model import MessageModel, UpdateMessage
from user_view import User

from .middlewares import authorized
from .responses import error, success


@authorized
async def get_paged_incoming_requests(user: User, page: int):
    users = await user.paged_incoming_requests(page)
    return success(users)


@authorized
async def get_paged_outgoing_requests(user: User, page: int):
    users = await user.paged_outgoing_requests(page)
    return success(users)


@authorized
async def get_paged_friends(user: User, page: int):
    users = await user.paged_friends(page)
    return success(users)


@authorized
async def get_paged_blocked(user: User, page: int):
    users = await user.paged_blocked(page)
    return success(users)


@authorized
async def send_friend_request(user: User, id: str):
    """
    Requests: id of reciever of friend request  
    Response: 200, 403, 404
    """

    try:
        id = ObjectId(id)
        await user.send_friend_request(id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.InvalidUser:
        return error("You can't send friend request to this user", 403)

    except user.exc.UnavailableForBots:
        return error("You are the bot user", 403)

    return success("ok")


@authorized
async def send_friend_code_request(user: User):
    """
    Requests: code as url param of reciever of friend request  
    Response: 200, 400, 404
    """

    try:
        friend_code = request.args.get('code', '')
        if not len(friend_code) or len(friend_code) > 50:
            return error("No friend code given", 400)

        await user.friend_code_request(friend_code)

    except User.exc.InvalidUser as err:
        return error(str(err), 403)

    except user.exc.UnavailableForBots:
        return error("You are the bot user", 403)

    return success("ok")


@authorized
async def response_friend_request(user: User, id: str):
    """
    Requests: id of friend request sender we're responding to  
    Optionally may set url param `accept` to True to accept (default: decline)  
    Response: 200, 400, 404
    """

    try:
        accept = request.args.get('accept', False) == "True"
        id = ObjectId(id)
        await user.response_friend_request(id, bool(accept))

    except bson_errors.InvalidId:
        return error("Invalid id", 400)

    except User.exc.UserNotInGroup:
        return error("User isn't in incoming requesters")

    except user.exc.UnavailableForBots:
        return error("You are the bot user", 403)

    return success("ok")


@authorized
async def cancel_friend_request(user: User, id: str):
    """
    Requests: id of user we sent request to cancel  
    Response: 200, 400, 403, 404
    """

    try:
        id = ObjectId(id)
        await user.cancel_friend_request(id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.UserNotInGroup:
        return error("User wasn't sent a friend request", 400)

    except user.exc.UnavailableForBots:
        return error("You are the bot user", 403)

    return success("ok")


@authorized
async def delete_friend(user: User, id: str):
    """
    Requests: id of reciever of friend request  
    Response: 200, 400, 404
    """

    try:
        id = ObjectId(id)
        await user.delete_friend(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except User.exc.UserNotInGroup:
        return error("User isn't your friend", 400)

    except user.exc.UnavailableForBots:
        return error("You are the bot user", 403)

    return success("ok")


@authorized
async def block_user(user: User, id: str):
    """
    Request: blocking user id in url  
    Response: 200, 204 (already blocked), 404
    """

    try:
        id = ObjectId(id)
        await user.block_user(id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except User.exc.UserNotInGroup:
        return success("User is blocked already", 204)

    return success("ok")


@authorized
async def unblock_user(user: User, id: str):
    """
    Request: unblocking user id in url  
    Response: 200, 204 (already blocked), 404
    """

    try:
        id = ObjectId(id)
        await user.unblock_user(id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except User.exc.UserNotInGroup:
        return success("User isn't blocked", 204)

    return success("ok")
