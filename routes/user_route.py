from app import app, config
from bson import ObjectId
from bson import errors as  bson_errors
from quart import Response, request, jsonify

from views import User

from .middlewares import (
    validate_schema,
    authorized
)

from .responces import (
    success, warning, error
)

from .schemas import (
    login, registrate, text_status
)


#? Users most important endpoints
@app.route("/api/user/login", methods=["POST"])
@validate_schema(login)
async def user_login():
    auth = await request.json

    try:
        user = await User.authorize(
            auth['login'],
            auth['password']
        )

    except:
        return error("Invalid credentials", 401)

    response = success({"user": user.private_dict})
    response.set_cookie(
        "token", user.token,
        max_age=48*60*60,
        # Patch for testing locally
        # If setted to secure - cookies can be used only via https
        secure=not config['DEBUG']
    )
    return response

@app.route("/api/user/logout", methods=["POST", "GET", "DELETE"])
@authorized
async def logout(user: User):
    user.logout()
    request.delete_cookie('token')
    return success("All is fine!")


@app.route("/api/user/register", methods=["POST"])
@validate_schema(registrate)
async def user_create():
    reg = await request.json
    try:
        user = await User.registrate(
            reg['nick'], reg['login'], reg['password']
        )

    except ValueError:
        return error("Login is already in use", 403)

    response = success(user.private_dict)
    response.set_cookie(
        "token", user.token,
        max_age=48*60*60,
        # Patch for testing locally
        # If setted to secure - cookies can be used only via https
        secure=not config['DEBUG']
    )

    return response

@app.route("/api/user/<string:id>")
@authorized
async def user_from_id(user: User, id: str):
    try:
        id = ObjectId(id)
        user_repr = await User.from_id(id)

    except User.exc.InvalidUser:
        return error("Invalid user id", 400)

    return success(user_repr.public_dict)


@app.route("/api/user/me")
@authorized
async def self_info(user: User):
    return success(user.private_dict)


#? Other endpoints
## Setters
@app.route("/api/me/nick", methods=["POST"])
@authorized
async def set_nickname(user: User):
    nickname = request.args.get('new_nick', '')
    try:
        await user.set_nickname(nickname)

    except ValueError:
        return error("Invalid nick", 400)

    return success(nickname)


@app.route("/api/me/nick", methods=["POST"])
@authorized
async def set_friend_code(user: User):
    friendcode = request.args.get('code', '')
    try:
        await user.set_friend_code(friendcode)
        return success(friendcode)

    except ValueError as ve:
        return error(ve, 400)



@app.route("/api/me/status/<int:new_status>", methods=["POST"])
@authorized
async def set_status(user: User, new_status: int):
    try:
        await user.set_status(new_status)
        return success("ok")

    except ValueError:
        return error("Wrong status code", 400)


@app.route("/api/me/text_status", methods=["POST"])
@authorized
@validate_schema(text_status)
async def set_text_status(user: User):
    text_status = await request.json.get('text_status')
    try:
        await user.set_text_status(text_status)
        return success('ok')

    except ValueError:
        return error("Invalid text status", 400)


## Friends
@app.route("/api/friends")
@authorized
async def get_users_friends(user: User):
    friends = await user.get_friends()
    return success(friends)


@app.route("/api/outgoing_requests")
@authorized
async def outgoing_requests(user: User):
    return success(user.pendings_outgoing)


@app.route("/api/incoming_requests")
@authorized
async def incoming_requests(user: User):
    return success(user.pendings_incoming)


@app.route("/api/friends/<string:id>", methods=["POST"])
@authorized
async def send_friend_request(user: User, id: str):
    try:
        id = ObjectId(id)
        await user.send_friend_request(id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.InvalidUser:
        return error("You can't send friend request to this user", 403)

    return success("ok")


@app.route("/api/friends/<string:id>", methods=["DELETE"])
@authorized
async def delete_friend(user: User, id: str):
    try:
        id = ObjectId(id)
        await user.delete_friend(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except User.exc.UserNotInGroup:
        return error("User isn't your friend", 400)

    return success("ok")


@app.route("/api/friends/request", methods=["POST"])
@authorized
async def send_code_friend_request(user: User):
    try:
        code = request.args.get('code', '')
        if not len(code) or len(code) > 50:
            raise ValueError("Invalid code", 400)

        await user.friend_code_request(code)

    except User.exc.InvalidUser as err:
        return error(str(err), 403)

    except ValueError:
        return error("No friend code given", 400)


@app.route("/api/incoming_requests/<string:id>", methods=["POST"])
@authorized
async def response_friend_request(user: User, id: str):
    try:
        accept = request.args.get('accept', 'True') == 'True'
        id = ObjectId(id)
        await user.response_friend_request(id, bool(accept))

    except bson_errors.InvalidId:
        return error("Invalid id")

    except User.exc.UserNotInGroup:
        return error("User isn't in incoming requesters")

    return success("ok")


@app.route("/api/outgoing_requests/<string:id>", methods=["DELETE"])
@authorized
async def cancel_friend_request(user: User, id: str):
    try:
        id = ObjectId(id)
        await user.cancel_friend_request(id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.UserNotInGroup:
        return error("User wasn't sent a friend request", 400)

    return success("ok")


## Blocked users
@app.route("/api/blocked")
@authorized
async def blocked_users(user: User):
    blocked_users = await user.batch_get_blocked()
    return success(blocked_users)


@app.route("/api/blocked/<string:id>", methods=["POST"])
@authorized
async def block_user(user: User, id: str):
    try:
        id = ObjectId(id)
        await user.block_user(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except User.exc.UserNotInGroup:
        return success("User is blocked already", 204)

    return success("ok")


@app.route("/api/blocked/<string:id>", methods=["DELETE"])
@authorized
async def unblock_user(user: User, id: str):
    try:
        id = ObjectId(id)
        await user.unblock_user(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except User.exc.UserNotInGroup:
        return success("User isn't blocked", 204)

    return success("ok")
