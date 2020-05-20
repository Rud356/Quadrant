from app import app
from bson import ObjectId
from bson import errors as  bson_errors
from quart import Response, request, jsonify
from views import UserView
from .middlewares import (
    validate_api_version,
    validate_schema,
    authorized
)
from .responces import (
    success, warning, error
)
from .schemas import (
    login, registrate, text_status
)


#TODO: change all error codes to some fine
@app.route("/api/users/login", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(login)
async def user_login():
    auth = await request.json
    try:
        user = await UserView.authorize(auth['login'], auth['password'])
    except:
        return error("Invalid credentials", 401)
    else:
        responce = success({"user": user.private_dict})
        responce.set_cookie("token", user.token, secure=True, max_age=48*60*60)
        return responce


@app.route("/api/users/register", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(registrate)
async def user_create():
    reg = await request.json
    if reg.get('parent') and reg.get('bot'):
        try:
            reg['parent'] = ObjectId(reg['parent'])

        except bson_errors.InvalidId:
            return error("Invalid parent id", 400)

    try:
        new_user = await UserView.create_user(**reg)
        responce = success({"user": new_user.private_dict})
        responce.set_cookie("token", new_user.token, secure=True, max_age=48*60*60)
        return responce

    except ValueError as ve:
        return error(ve, 403)


@app.route("/api/users/me")
@validate_api_version("1.0.0")
@authorized
async def about_me(user: UserView):
    return success(user.private_dict())


@app.route("/api/me/nick", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def set_nickname(user: UserView):
    nickname = request.args.get('new_nick', '')
    try:
        user.set_nickname(nickname)
        return success(nickname)

    except ValueError:
        return error("Incorrect nickname length (should be in range from 1 to 50)", 400)


@app.route("/api/me/friendcode", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def set_friendcode(user: UserView):
    friendcode = request.args.get('code', '')
    try:
        await user.set_friend_code(friendcode)
        return success(friendcode)

    except ValueError as ve:
        return error(ve, 400)


@app.route("/api/me/text_status", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(text_status)
@authorized
async def set_text_status(user: UserView):
    text_status = await request.get('text_status')
    try:
        await user.set_text_status(text_status)
        return success("ok")
    except ValueError:
        return error("Too long text status", 400)


@app.route("/api/me/status/<int:new_status>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def set_status(user: UserView, new_status):
    try:
        await user.set_status(new_status)
        return success("ok")

    except ValueError:
        return error("Invalid status", 400)


@app.route("/api/users/me/logout")
@validate_api_version("1.0.0")
@authorized
async def logout(user: UserView):
    await user.logout()
    #TODO: drop token from cookies
    return success("All is fine!")


@app.route("/api/users/<string:id>")
@validate_api_version("1.0.0")
@authorized
async def user_from_id(user: UserView, id: str):
    try:
        id = ObjectId(id)
        user_repr = await UserView.from_id(id)
        return success(user_repr.public_dict)

    except UserView.exc.InvalidUser:
        return error("Invalid user id", 400)


#? friends
@app.route("/api/friends")
@validate_api_version("1.0.0")
@authorized
async def get_users_friends(user: UserView):
    #TODO: somehow optimize this operation later
    friends = await user.batch_get_friends()
    return success(friends)


@app.route("/api/friends/<string:id>")
@validate_api_version("1.0.0")
@authorized
async def user_from_friends(user: UserView, id: str):
    try:
        id = ObjectId(id)
        if id not in user.friends:
            raise ValueError("User isn't a friend of yours")

        user_repr = await UserView.from_id(id)
        return success(user_repr.public_dict)

    except (UserView.exc.InvalidUser, bson_errors.InvalidId):
        return error("Invalid user id")

    except ValueError:
        return error("User isn't your friend", 400)


@app.route("/api/friends/<string:id>", methods=["DELETE"])
@validate_api_version("1.0.0")
@authorized
async def delete_friend(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.delete_friend(id)
        return success("ok")

    except bson_errors.InvalidId:
        return error("No user with this id")

    except UserView.exc.UserNotInGroup:
        return error("User isn't your friend", 400)


##? friends requests and all related
@app.route("/api/friends/<string:id>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def send_friend_request(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.send_friend_request(id)
        return success("ok")

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.InvalidUser:
        return error("You can't send friend request to this user", 403)


@app.route("/api/friends", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def send_friend_request_code(user: UserView):
    try:
        code = request.args.get('code')
        if not code:
            raise ValueError("Too short code")

        await user.frined_code_request(code)
        return success("ok")

    except ValueError:
        return error("Invalid friend code", 400)

    except user.exc.InvalidUser:
        return error("You can't send friend request to this user", 403)


#TODO: add batches to two bethods below
@app.route("/api/friend_requests")
@validate_api_version("1.0.0")
@authorized
async def outgoing_requests(user: UserView):
    return success(user.pendings_outgoing)


@app.route("/api/pending_requests")
@validate_api_version("1.0.0")
@authorized
async def incoming_pendings(user: UserView):
    return success(user.pendings_incoming)


@app.route("/api/friend_requests/<string:id>", methods=["DELETE"])
@validate_api_version("1.0.0")
@authorized
async def cancel_friend_request(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.cancel_friend_request(id)
        return success("ok")

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.UserNotInGroup:
        return error("User wasn't sent a friend request", 400)


@app.route("/api/pending_requests/<string:id>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def responce_friend_request(user: UserView, id: str):
    try:
        # workaround not being able to get bool out of string
        # default value is True
        accept = request.args.get('accept', 'True') == 'True'
        id = ObjectId(id)
        await user.responce_friend_request(id, bool(accept))
        return success("ok")

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.UserNotInGroup:
        return error("This user isn't pending your responce on friendship", 400)

    except ValueError:
        return error("Invalid accept parameter in url", 400)

#? blocked users
@app.route("/api/blocked")
@validate_api_version("1.0.0")
@authorized
async def blocked_users(user: UserView):
    #TODO: optimize this one too
    blocked_repr = await user.batch_get_blocked()
    return success(blocked_repr)


@app.route("/api/blocked/<string:id>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def block_user(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.block_user(id)
        return success("ok")

    except bson_errors.InvalidId:
        return error("No user with this id")

    except UserView.exc.UserNotInGroup:
        return success("User is blocked already", 204)


@app.route("/api/blocked/<string:id>", methods=["DELETE"])
@validate_api_version("1.0.0")
@authorized
async def unblock_user(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.unblock_user(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except UserView.exc.UserNotInGroup:
        return success("User isn't blocked", 204)

    else:
        return success("ok")

