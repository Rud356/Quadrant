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


@app.route("/api/users/login")
@validate_api_version("1.0.0")
@validate_schema(login)
async def user_login():
    auth = await request.json()
    user = await UserView.authorize(auth['login'], auth['password'])
    responce = Response("Success!", 200)
    responce.set_cookie("token", user.token, secure=True, max_age=48*60*60)
    return responce


@app.route("/api/users/register")
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


@app.route("/api/users/logout")
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