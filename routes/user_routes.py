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
    login, registrate
)
#TODO: change all error codes to some fine
#TODO: add way for user getting info about himself
@app.route("/api/users/login", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(login)
async def user_login():
    auth = await request.json
    try:
        user = await UserView.authorize(auth['login'], auth['password'])
    except:
        return error("Invalid credentials")
    else:
        #TODO: fix giving cookies
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

        #TODO: add responce
    try:
        new_user = await UserView.create_user(**reg)
    except:
        return error("You can't registrate account with that login")

    else:
        responce = success({"user": new_user.private_dict})
        responce.set_cookie("token", new_user.token, secure=True, max_age=48*60*60)
        return responce


@app.route("/api/users/my")
@validate_api_version("1.0.0")
@authorized
async def about_me(user: UserView):
    return user.private_dict()


@app.route("/api/users/my/logout")
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
@app.route("/api/users/my/friends")
@validate_api_version("1.0.0")
@authorized
async def get_users_friends(user: UserView):
    #TODO: somehow optimize this operation later
    friends = await user.batch_get_friends()
    return success(friends)


@app.route("/api/users/my/friends/<string:id>")
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
        return error("Invalid user id", 400)

    except ValueError:
        return error("User isn't your friend")


@app.route("/api/users/my/friends/<string:id>", methods=["DELETE"])
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
        return error("User isn't your friend")


##? friends requests and all related
@app.route("/api/users/my/friends/<string:id>", methods=["POST"])
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
        return error("You can't send friend request to this user")


@app.route("/api/users/my/friends/code?=<string:code>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def send_friend_request_code(user: UserView, code: str):
    try:
        await user.frined_code_request(code)
        return success("ok")

    except ValueError:
        return error("Invalid friend code")

    except user.exc.InvalidUser:
        return error("You can't send friend request to this user")


#TODO: add batches to two bethods below
@app.route("/api/users/my/requests")
@validate_api_version("1.0.0")
@authorized
async def outgoing_requests(user: UserView):
    #TODO: maybe add batch request
    return success(user.pendings_outgoing)


@app.route("/api/users/my/pendings")
@validate_api_version("1.0.0")
@authorized
async def incoming_pendings(user: UserView):
    return success(user.pendings_incoming)


@app.route("/api/users/my/requests/<string:id>", methods=["DELETE"])
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
        return error("User wasn't sent a friend request")


@app.route("/api/users/my/pendings/<string:id>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def responce_friend_request(user: UserView, id: str):
    try:
        accept = bool(request.args.get('accept', 1))
        id = ObjectId(id)
        await user.responce_friend_request(id, bool(accept))
        return success("ok")

    except bson_errors.InvalidId:
        return error("Invalid id")

    except user.exc.UserNotInGroup:
        return error("This user isn't pending your responce on friendship")


#? blocked users
@app.route("/api/users/my/blocked")
@validate_api_version("1.0.0")
@authorized
async def blocked_users(user: UserView):
    #TODO: optimize this one too
    blocked_repr = await user.batch_get_blocked()
    return success(blocked_repr)


@app.route("/api/users/my/blocked/<string:id>", methods=["POST"])
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
        return error("User is blocked already")


@app.route("/api/users/my/blocked/<string:id>", methods=["DELETE"])
@validate_api_version("1.0.0")
@authorized
async def unblock_user(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.unblock_user(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except UserView.exc.UserNotInGroup:
        return error("User isn't blocked")

    else:
        return success("ok")

#TODO: add setting users things
