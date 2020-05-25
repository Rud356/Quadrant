from app import app
from bson import ObjectId
from bson import errors as  bson_errors
from quart import Response, request, jsonify

from views import User
from models import TextEndpoint, DMChannel

from .middlewares import (
    validate_schema,
    authorized
)
from .responces import (
    success, warning, error
)
from .schemas import (
    dm_endpoint
)


@app.route("/api/endpoints")
@authorized
async def get_endpoints(user: User):
    endpoints = await user.get_endpoints()
    endpoints_views = [endpoint.__dict__ for endpoint in endpoints]

    return success(endpoints_views)


@app.route("/api/endpoints/<string:endpoint_id>")
@authorized
async def get_endpoint(user: User, endpoint_id):
    try:
        endpoint = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint)

        return success(endpoint.__dict__)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("Invalid endpoint")


@app.route("/api/endpoints/create_endpoint/dm", methods=["POST"])
@authorized
async def create_dm(user: User):
    try:
        with_user = ObjectId(await request.json['with'])
        new_endpoint = await DMChannel.create_endpoint(user._id, with_user)
        # Send to second user if online info about new endpoint
        return success({"endpoint": new_endpoint.__dict__})

    except bson_errors.InvalidId:
        return error("Invalid user with id")

    except ValueError as ve:
        return error(ve, 409)
