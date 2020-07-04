from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app
from models.enums import UpdateType
from models.message_model import MessageModel, UpdateMessage
from user_view import User

from .middlewares import authorized, validate_schema
from .responces import error, success
from .schemas import login, registrate, text_status


@validate_schema(login)
async def authorize_user():
    """
    Payload:
    {
        "login": "string",
        "password": "string"
    }
    Response: 200 private user + token cookie, 401
    """

    auth = await request.json

    try:
        user = await User.authorize(
            auth['login'],
            auth['password'],
            request.cookies.get('token')
        )

    except ValueError:
        return error("Invalid credentials", 401)

    response = success({"user": user.private_dict})
    # Patch for testing locally
    # If setted to secure - cookies can be used only via https
    response.set_cookie(
        "token", user.token,
        max_age=48 * 60 * 60,
        secure=not app.config['DEBUG']
    )
    return response


@authorized
async def logout_user(user: User):
    """
    Requires authorization!
    Response: "All is fine!" 200
    """

    user.logout()
    response = success("All is fine!")
    response.delete_cookie('token')
    return response


@app.route("/api/user/keep-alive")
@authorized
async def keep_alive(user: User):
    """
    Response: ok
    """

    return success("ok")


@validate_schema(registrate)
async def registrate_user():
    """
    Payload:
    {
        "login": "string",
        "password": "string",
        "nick": "string"
    }

    Validations:  
    `0 < nick length <= 25`  
    `5 < login length <= 200`  
    `8 < password length <= 255`  
    If they're failed - returns code 400  

    Repsonse: 400, 403 or 200 private user + token cookie
    """

    reg = await request.json

    if not app.config["ALLOW_REG"]:
        return error("Sorry, but you can't register", 403)

    nick = reg['nick'].replace(' \n\t', '')
    login = reg['login'].replace(' \n\t', '')
    password = reg['password'].replace(' \n\t', '')

    if len(nick) not in range(1, 25 + 1):
        return error("Invalid nick", 400)

    if len(login) not in range(5, 201):
        return error("Invalid login length", 400)

    if len(password) not in range(8, 256):
        return error("Invalid password length", 400)

    try:
        user = await User.registrate(
            nick, login, password
        )

    except ValueError:
        return error("Login is already in use", 403)

    response = success(user.private_dict)
    response.set_cookie(
        "token", user.token,
        max_age=48 * 60 * 60,
        # Patch for testing locally
        # If setted to secure - cookies can be used only via https
        secure=not app.config['DEBUG']
    )

    return response


@authorized
async def user_from_id(user: User, id: str):
    """
    Requires: user id in route  
    Response: 400 or public user
    """

    try:
        id = ObjectId(id)
        user_object = await User.from_id(id)

    except (User.exc.InvalidUser, bson_errors.InvalidId):
        return error("Invalid user id", 400)

    return success(user_object.public_dict)


@authorized
async def user_about_self(user: User):
    """
    Response: private user
    """

    return success(user.private_dict)

# Setters
@authorized
async def set_nickname(user: User):
    """
    Requires: new_nick as url parameter  
    Validations:  
    `0 < nick length <= 25`  
    Responses: 200, 400
    """

    nickname = request.args.get('new_nick', '')
    try:
        await user.set_nick(nickname)

    except ValueError:
        return error("Invalid nick", 400)

    updated_nick = UpdateMessage(
        {
            "user_id": user._id,
            "nick": nickname
        },
        UpdateType.updated_nick
    )
    await user.broadcast_to_friends(updated_nick)
    return success("ok")


@authorized
async def set_friend_code(user: User):
    """
    Requires: code as url parameter  
    Validations:  
    `0 < code length <= 50`  
    Responses: 200, 400
    """

    friendcode = request.args.get('code', '')
    try:
        await user.set_friend_code(friendcode)
        return success(friendcode)

    except ValueError as ve:
        return error(str(ve), 400)

    except user.exc.UnavailableForBots:
        return error("You are the bot user", 403)


@authorized
async def set_status(user: User, new_status: int):
    """
    Requires: status code in url  
    Validations:  
    `0 <= status <= 4`  
    Responses: 200, 400
    """

    try:
        await user.set_status(new_status)

    except ValueError:
        return error("Wrong status code", 400)

    updated_status = UpdateMessage(
        {
            "user_id": user._id,
            "status": new_status
        },
        UpdateType.updated_status
    )
    await user.broadcast_to_friends(updated_status)
    return success("ok")


@authorized
@validate_schema(text_status)
async def set_text_status(user: User):
    """
    Requries:
    {
        "text_status": "string" or empty string
    }  
    Response: 200, 400
    """

    text_status = await request.json
    text_status = text_status.get('text_status')
    try:
        await user.set_text_status(text_status)

    except ValueError:
        return error("Invalid text status", 400)

    updated_text_status = UpdateMessage(
        {
            "user_id": user._id,
            "status": text_status
        },
        UpdateType.updated_status
    )
    await user.broadcast_to_friends(updated_text_status)
    return success('ok')


# Dangerous methods for user
@authorized
async def update_users_token(user: User):
    await user.update_token()
    user.logout()

    response = success('ok')
    response.delete_cookie('token')

    return response


@authorized
async def delete_user(user: User):
    await user.delete_user()
    user.logout()
    response = success('ok')
    response.delete_cookie('token')
    return response
