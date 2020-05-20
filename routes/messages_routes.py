from app import app
from bson import ObjectId
from bson import errors as  bson_errors
from quart import Response, request, jsonify
from views import UserView, users_connected_ids
from models.endpoint import TextEndpoint
from .middlewares import (
    validate_api_version,
    validate_schema,
    authorized
)
from .responces import (
    success, warning, error
)
from .schemas import (
    message
)


@app.route("/api/endpoints/<string:endpoint_id>/messages")
@validate_api_version("1.0.0")
@authorized
async def get_messages_latest(user: UserView, endpoint_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_messages(user._id, endpoint.last_message)
        return success({"messages":[message.__dict__ for message in messages]})

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages/from/<string:message_id>")
@validate_api_version("1.0.0")
@authorized
async def get_messages_from(user: UserView, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        messages = await endpoint.get_messages(user._id, endpoint.last_message)
        return success({"messages":[message.__dict__ for message in messages]})

    except TextEndpoint.exc.NotGroupMember:
        return error("You aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>")
@validate_api_version("1.0.0")
@authorized
async def get_message(user: UserView, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        message = await endpoint.get_message(user._id, message_id)
        # resend to all members
        return success({"message":message.__dict__})

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>", methods=["PATCH"])
@validate_api_version("1.0.0")
@validate_schema(message)
@authorized
async def edit_message(user: UserView, endpoint_id: str, message_id: str):
    try:
        content = await request.json['content']
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        message_modified = await endpoint.edit_message(user._id, message_id, content)

        #TODO resend to all members that message updated
        return success({"message_edited": message_modified})

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")

# TODO: add get pins
@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>/pin", methods=["PATCH"])
@validate_api_version("1.0.0")
@authorized
async def set_pin_state_message(user: UserView, endpoint_id: str, message_id: str):
    try:
        pinned = request.args.get('accept', 'False') == 'True'
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        message_pinned = await endpoint.pin_message(user._id, message_id, pinned)

        #TODO resend to all members that message updated
        if message_pinned:
            return success({"message_pinned": message_id})

        else:
            return error("Nothing was pinned, no permissions", 403)

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")


@app.route("/api/endpoints/<string:endpoint_id>/messages", methods=["POST"])
@validate_api_version("1.0.0")
@validate_schema(message)
@authorized
async def post_message(user: UserView, endpoint_id: str):
    try:
        data = await request.json
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message = await endpoint.send_message(user._id, **data)
        for user_id in endpoint.members:

            user: UserView = users_connected_ids.get(user_id, None)

            if not user:
                continue

            user.message_queue.append(message)

        return success({"message":message.__dict__})

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except ValueError:
        return error("Too long message", 400)


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>", methods=["DELETE"])
@validate_api_version("1.0.0")
@authorized
async def delete_message(user: UserView, endpoint_id: str, message_id: str):
    try:
        force_delete = bool(request.args.get('force', False))

        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.small_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint or incorrect id", 400)

    try:
        message_id = ObjectId(message_id)
        if not force_delete:
            message = await endpoint.delete_message(user._id, message_id)
        else:
            message = await endpoint.force_delete(user._id, message_id)
        #TODO: resend to all members
        return success({"deleted": message})

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")

    except endpoint.exc.EndpointException:
        return error("You can't force delete this message", 403)
