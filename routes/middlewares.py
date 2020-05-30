import json

import fastjsonschema
from quart import request, websocket

from views import User

from .responces import error


def authorized(f):
    async def wraps(*args, **kwargs):
        if not request.cookies.get('token'):
            return error("You have to authorize first", 401)

        try:
            user = await User.authorize(token=request.cookies.get('token'))

        except TypeError as e:
            print(e)
            return error("User unauthorized", 401)

        return await f(*args, user=user, **kwargs)

    wraps.__name__ = f.__name__
    return wraps


def validate_schema(schema: object):
    def wrapper(f):
        async def wraps(*args, **kwargs):
            try:
                json_data = await request.json
                schema(json_data)

            except fastjsonschema.JsonSchemaException:
                return error("You sent invalid json", 400)

            else:
                return await f(*args, **kwargs)

        wraps.__name__ = f.__name__
        return wraps

    return wrapper


def auth_websocket(f):
    async def wraps(*args, **kwargs):
        auth = await websocket.data()
        try:
            auth = json.loads(auth)
            user = await User.authorize(token=auth['token'])

        except ValueError:
            return error("Incorrect credentials", 401)

        except KeyError:
            return error("No token provided", 401)

        return await f(*args, **kwargs, user=user)
    wraps.__name__ = f.__name__
    return wraps
