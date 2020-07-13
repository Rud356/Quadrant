from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app
from models.enums import UpdateType
from models.message_model import UpdateMessage
from user_view import User
from utils import string_strips

from .middlewares import authorized, validate_schema
from .responses import error, success
from .schemas import registrate_bot


@authorized
async def get_bots(user: User):
    bots = await user.get_bots()
    return success(bots)


@authorized
@validate_schema(registrate_bot)
async def registrating_bot(user: User):
    data = await request.json

    if user.bot:
        return error("You're a bot", 403)

    try:
        new_bot = user.registrate_bot(data['nick'])

    except ValueError:
        return error("You have too many bots", 400)

    bot_dict = new_bot.private_dict
    bot_dict.update({'token': new_bot.token})

    return success(bot_dict)


@authorized
async def change_nick(user: User, bot_id: str, nick: str):
    try:
        bot_id = ObjectId(bot_id)

    except bson_errors.InvalidId:
        return error("Invalid user id", 400)

    bot: User = user.from_id(bot_id)
    nick = string_strips(nick)

    if bot.parent == user._id:

        if len(nick) in range(1, 26):
            return error("Invalid nick length", 400)

        await bot.update(nick=nick)

    updated_nick = UpdateMessage(
        {
            "_id": user._id,
            "nick": nick
        },
        UpdateType.updated_nick
    )
    await bot.add_message(updated_nick)
    return success("ok")


@authorized
async def update_token(user: User, bot_id: str):
    try:
        bot_id = ObjectId(bot_id)

    except bson_errors.InvalidId:
        return error("Invalid user id", 400)

    bot: User = user.from_id(bot_id)

    if bot.parent == user._id:
        await bot.update_token()

    token = bot.token
    bot.logout()
    return success({'new_token': token})


@authorized
async def delete_bot(user: User, bot_id: str):
    try:
        bot_id = ObjectId(bot_id)

    except bson_errors.InvalidId:
        return error("Invalid user id", 400)

    bot: User = user.from_id(bot_id)

    if bot.bot and bot.parent == user._id:
        await bot.delete_user()

    return success("ok")
