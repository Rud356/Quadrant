import fastjsonschema
from quart import Response, request

from app import server_api_version
from api_version import APIVersion

from views import UserView
from .responces import success, warning, error


def authorized(f):
    async def wraps(*args, **kwargs):
        if not request.cookies.get('token'):
            print(request.cookies)
            #TODO: fix this part
            return """
            Before going to this page you have to visit <a href="/set_name/sample"></a>
            """

        try:
            user = await UserView.authorize(token=request.cookies.get('token'))

        except TypeError:
            return await error("User unauthorized", 401)

        return await f(*args, user=user, **kwargs)

    wraps.__name__ = f.__name__
    return wraps


def validate_api_version(required: str):
    required = APIVersion.from_str(required)

    def wrapper(f):
        async def wraps(*args, **kwargs):
            if not request.headers.get('api_version'):
                return await error("To be able to use api you have to set its version", 400)

            try:
                api_users = APIVersion.from_str(request.headers.get('api_version'))

            except ValueError:
                return await error("Invalid api version", 405)

            if required > api_users:
                return await warning("Your api version is unsupproted by this method")

            return await f(*args, **kwargs)

        wraps.__name__ = f.__name__
        return wraps

    return wrapper


def validate_schema(schema: object):
    def wrapper(f):
        async def wraps(*args, **kwargs):
            try:
                schema(await request.json)

            except fastjsonschema.JsonSchemaException:
                return await error("You sent invalid json", 400)

            else:
                return await f(*args, **kwargs)

        wraps.__name__ = f.__name__
        return wraps

    return wrapper
