from app import app
from bson import ObjectId
from bson import errors as  bson_errors
from quart import Response, request, jsonify

from views import User, connected_users
from models import MetaEndpoint, ChannelType, TextEndpoint

from .middlewares import (
    validate_schema,
    authorized
)
from .responces import (
    success, warning, error
)
from .schemas import (
    message
)

#? Fetching messages
@app.route("/api/endpoints/<string:endpoint_id>/messages")
@authorized
async def get_messages_latest(user: User, endpoint_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_messages(user._id)
        return success(
            {"messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>/from")
@authorized
async def get_messages_from(user: User, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        message_id = ObjectId(message_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_messages_from(user._id, message_id)
        return success(
            {"messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>/after")
@authorized
async def get_messages_after(user: User, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        message_id = ObjectId(message_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_messages_after(user._id, message_id)
        return success(
            {"messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages/pinned")
@authorized
async def get_pinned_latest(user: User, endpoint_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_pinned_messages(user._id)
        return success(
            {"messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>/pinned/from")
@authorized
async def get_pinned_messages_from(user: User, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        message_id = ObjectId(message_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_pinned_messages_from(user._id, message_id)
        return success(
            {"messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages", methods=["POST"])
@authorized
@validate_schema(message)
async def post_message(user: User, endpoint_id: str):
    try:
        data = await request.json
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message = await endpoint.send_message(user._id, **data)
        for user_id in endpoint.members:

            user: User = connected_users.get(user_id, None)
            if not user:
                continue

            user.message_queue.append(message)

        return success({"message":message.__dict__})

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except ValueError:
        return error("Too long message", 400)


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>", methods=["DELETE"])
@authorized
async def delete_message(user: User, endpoint_id: str, message_id: str):
    try:
        force_delete = bool(request.args.get('force', False))

        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint or incorrect id", 400)


    try:
        message_id = ObjectId(message_id)
        if not force_delete:
            message = await endpoint.delete_message(user._id, message_id)

        else:
            message = await endpoint.force_delete_message(user._id, message_id)

        #TODO: resend to all members
        return success({"deleted": message})

    except bson_errors.InvalidId:
        return error("Invalid message id")

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except NotImplementedError:
        return error("You can't force delete this message", 403)


@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>", methods=["PATCH"])
@authorized
@validate_schema(message)
async def edit_message(user: User, endpoint_id: str, message_id: str):
    try:
        content = await request.json['content']
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

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
        return error("You aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")



@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>/pin", methods=["PATCH"])
@authorized
async def pin_message(user: User, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        message_pinned = await endpoint.pin_message(user._id, message_id)

        #TODO resend to all members that message updated
        return success({"message_pinned": message_pinned})

    except TextEndpoint.exc.NotGroupMember:
        return error("You aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")

@app.route("/api/endpoints/<string:endpoint_id>/messages/<string:message_id>/unpin", methods=["PATCH"])
@authorized
async def unpin_message(user: User, endpoint_id: str, message_id: str):
    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        message_unpinned = await endpoint.unpin_message(user._id, message_id)

        #TODO resend to all members that message updated
        return success({"message_unpinned": message_unpinned})

    except TextEndpoint.exc.NotGroupMember:
        return error("You aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")
