from app import app
from bson import ObjectId
from bson import errors as  bson_errors
from quart import Response, request, jsonify
from views import UserView
from models.endpoint import TextEndpoint, DMchannel
from .middlewares import (
    validate_api_version,
    validate_schema,
    authorized
)
from .responces import (
    success, warning, error
)
from .schemas import (
    dm_endpoint
)


@app.route("/api/users/my/endpoints")
@validate_api_version("1.0.0")
@authorized
async def get_endpoints(user: UserView):
    endpoints = list(map(lambda endpoint: endpoint.__dict__, await user.endpoint()))
    return success(endpoints)


@app.route("/api/users/my/endpoints/<string:endpoint_id>")
@validate_api_version("1.0.0")
@authorized
async def get_endpoint(user: UserView, endpoint_id: str):
    try:
        endpoint = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint)

        return success(endpoint.__dict__)

    except bson_errors.InvalidId:
        return error("Invalid id")


@app.route("/api/users/my/endpoints/create_endpoint?=dm")
@validate_api_version("1.0.0")
@validate_schema(dm_endpoint)
@authorized
async def create_dm(user: UserView):
    try:
        with_user = ObjectId(await request.json['with'])
        new_endpoint = await DMchannel.create_endpoint(user._id, with_user)
        # send to second user if online info about new endpoint
        return success({"endpoint":new_endpoint.__dict__})

    except bson_errors.InvalidId:
        return error("Invalid user with id")


#TODO: create invites