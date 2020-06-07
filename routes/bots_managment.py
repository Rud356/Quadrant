from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app
from models import UpdateMessage, UpdateType
from views import User

from .middlewares import authorized, validate_schema
from .responces import error, success
from .schemas import registrate_bot


@app.route("/api/bots")
@authorized
async def get_bots(user: User):
    bots = await user.get_bots()
    return success(bots)


@app.route("/api/bots/registrate", methods=["POST"])
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


@app.route("/api/bots/<string:bot_id>/<string:nick>", methods=["POST"])
@authorized
async def change_nick(user: User, bot_id: str, nick: str):
    try:
        bot_id = ObjectId(bot_id)

    except bson_errors.InvalidId:
        return error("Invalid user id", 400)

    bot: User = user.from_id(bot_id)

    if bot.parent == user._id:
        try:
            await bot.set_nick(nick)

        except ValueError:
            return error("Invalid bot nick length")

    updated_nick = UpdateMessage(
        {
            "user_id": user._id,
            "nick": nick
        },
        UpdateType.updated_nick
    )
    await bot.add_message(updated_nick)
    return success("ok")


@app.route("/api/bots/<string:bot_id>/update_token", methods=["POST"])
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


@app.route("/api/bots/<string:bot_id>", methods=["DELETE"])
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


__all__ = [
    "get_bots", "registrating_bot", "delete_bot",
    "update_token", "change_nick"
]
