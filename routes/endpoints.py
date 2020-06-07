from typing import List

from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app
from models import DMChannel, TextEndpoint
from views import User

from .middlewares import authorized, validate_schema
from .responces import error, success
from .schemas import dm_endpoint


@app.route("/api/endpoints")
@authorized
async def get_endpoints(user: User):
    endpoints: List[ObjectId] = await user.get_endpoints()

    return success(endpoints)


@app.route("/api/endpoints/<string:endpoint_id>")
@authorized
async def get_endpoint(user: User, endpoint_id):
    try:
        endpoint = ObjectId(endpoint_id)
        endpoint: TextEndpoint = await user.get_endpoint(endpoint)

        return success(endpoint.__dict__)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("Invalid endpoint")


@app.route("/api/endpoints/create_endpoint/dm", methods=["POST"])
@authorized
@validate_schema(dm_endpoint)
async def create_dm(user: User):
    try:
        with_user = await request.json
        with_user = ObjectId(with_user['with'])
        new_endpoint: DMChannel = await DMChannel.create_endpoint(
            user._id,
            with_user
        )
        # Send to second user if online info about new endpoint
        return success({"endpoint": new_endpoint.__dict__})

    except bson_errors.InvalidId:
        return error("Invalid user with id")

    except ValueError as ve:
        return error(str(ve), 409)


__all__ = [
    "get_endpoints", "get_endpoint",
    "create_dm"
]
