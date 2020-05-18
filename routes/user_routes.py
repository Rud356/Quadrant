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


@app.route("/api/users/login", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(login)
async def user_login():
    auth = await request.json()
    user = await UserView.authorize(auth['login'], auth['password'])
    responce = Response("Success!", 200)
    responce.set_cookie("token", user.token, secure=True, max_age=48*60*60)
    return responce


@app.route("/api/users/register", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(registrate)
async def user_create():
    reg = await request.json()
    if reg.get('parent') and reg.get('bot'):
        try:
            reg['parent'] = ObjectId(reg['parent'])

        except bson_errors.InvalidId:
            return error("Invalid parent id", 400)

    new_user = await UserView.create_user(**reg)
    responce = Response("Registrated!", 200)
    responce.set_cookie("token", new_user.token, secure=True, max_age=48*60*60)
    return responce


@app.route("/api/users/logout", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def logout(user: UserView):
    await user.logout()
    return success("All is fine!")


@app.route("/api/users/<string:id>")
@validate_api_version("1.0.0")
@authorized
async def user_from_id(user: UserView, id: str):
    try:
        id = ObjectId(id)
        user_repr = await UserView.from_id(id)

    except UserView.exc.InvalidUser:
        return error("Invalid user id", 400)

    else:
        return success(user_repr.public_dict)


@app.route("/api/users/friends")
@validate_api_version("1.0.0")
@authorized
async def get_users_friends(user: UserView):
    #TODO: somehow optimize this operation later
    friends = await user.batch_get_friends()
    return success(friends)


@app.route("/api/users/friends/<string:id>")
@validate_api_version("1.0.0")
@authorized
async def user_from_friends(user: UserView, id: str):
    try:
        id = ObjectId(id)
        if id not in user.friends:
            raise ValueError("User isn't a friend of yours")

        user_repr = await UserView.from_id(id)

    except (UserView.exc.InvalidUser, bson_errors.InvalidId):
        return error("Invalid user id", 400)

    except ValueError:
        return error("User isn't your friend")

    else:
        return success(user_repr.public_dict)


@app.route("/api/users/friends/<string:id>", methods=["DELETE"])
@validate_api_version("1.0.0")
@authorized
async def delete_friend(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.delete_friend(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except UserView.exc.UserNotInGroup:
        return error("User isn't your friend")

    else:
        return success("ok")


@app.route("/api/users/blocked")
@validate_api_version("1.0.0")
@authorized
async def blocked_users(user: UserView):
    blocked_repr = await user.batch_get_blocked()
    return success(blocked_repr)


@app.route("/api/users/blocked/<string:id>", methods=["POST"])
@validate_api_version("1.0.0")
@authorized
async def block_user(user: UserView, id: str):
    try:
        id = ObjectId(id)
        await user.block_user(id)

    except bson_errors.InvalidId:
        return error("No user with this id")

    except UserView.exc.UserNotInGroup:
        return error("User is blocked already")

    else:
        return success("ok")


@app.route("/api/users/blocked/<string:id>", methods=["DELETE"])
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
