from pathlib import Path

from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app, connected_users
from models.endpoint_model import TextEndpoint
from models.enums import UpdateType
from models.message_model import MessageModel as Message
from models.message_model import UpdateMessage
from user_view import User

from .middlewares import authorized, validate_schema
from .responces import error, success
from .schemas import message

files_path = Path(app.config['UPLOAD_FOLDER'])


async def broadcast_message(endpoint: TextEndpoint, message: Message):
    members = endpoint.members

    for member_id in members:
        member = connected_users.get(member_id)

        if member is None:
            continue

        await member.add_message(message)


@authorized
@validate_schema(message)
async def send_message(user: User, endpoint_id: str):
    """
    Requires: endpoint id, message id
    Payload:
    {
        "content": "string",
        "files": ["strings"]
    }
    Checks: message content length <= 3000 symbols
    Response: 200, 400, 403, 404
    """

    data = await request.json

    if not data['content'] and not data.get('files'):
        return error("No content given", 400)

    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    filtered_files = []
    for file in data.get('files', []):
        if (files_path / file).is_file():
            filtered_files.append(str(file))

    try:
        message = await endpoint.send_message(
            user._id, data.get('content'), filtered_files
        )
        for user_id in endpoint.members:

            user: User = connected_users.get(user_id, None)
            if not user:
                continue

            await broadcast_message(endpoint, message)

        return success("ok")

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except ValueError:
        return error("Too long message", 400)


@authorized
async def get_message(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id
    Response: 200 (message object), 403, 404
    """

    try:
        message_id = ObjectId(message_id)
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        message = await endpoint.get_message(user._id, message_id)
        return success(message)

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@authorized
async def get_messages_latest(user: User, endpoint_id: str):
    """
    Requires: endpoint id
    Response: 100 messages from last one including it
    """

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
            {
                "messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@authorized
async def get_messages_from(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id
    Response: 100 messages from setted one without it
    """

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
            {
                "messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@authorized
async def get_messages_after(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id
    Response: 100 messages after setted one without it
    """

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
            {
                "messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@authorized
async def get_pinned_latest(user: User, endpoint_id: str):
    """
    Requires: endpoint id
    Response: 100 pinned newest messages with newest one
    """

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
            {
                "messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@authorized
async def get_pinned_messages_from(
    user: User, endpoint_id: str, message_id: str
):
    """
    Requires: endpoint id, message id
    Response: 100 pinned messages from setted one excluding it
    """

    try:
        endpoint_id = ObjectId(endpoint_id)
        message_id = ObjectId(message_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid id")

    except ValueError:
        return error("No such endpoint")

    try:
        messages = await endpoint.get_pinned_messages_from(
            user._id, message_id
        )
        return success(
            {
                "messages":
                [message.__dict__ for message in messages]
            }
        )

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)


@authorized
async def delete_message(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id and
    optionally can have `force` url param (default is false)
    Response: 200, 204, 403, 404
    """
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

        if message:
            update_message = UpdateMessage(
                {
                    "deleted_message": message_id
                },
                UpdateType.deleted_message
            )
            await broadcast_message(endpoint, update_message)
            return success("ok")

        else:
            return success("Not deleted", 204)

    except bson_errors.InvalidId:
        return error("Invalid message id")

    except TextEndpoint.exc.NotGroupMember:
        return error("you aren't a group member", 403)

    except NotImplementedError:
        return error("You can't force delete this message", 403)

    except TextEndpoint.exc.NoPermission:
        return error("You can't perform this action", 403)


@authorized
@validate_schema(message)
async def edit_message(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id
    Payload:
    {
        "content": "string",
    }
    Checks: message content length <= 3000 symbols
    Response: 200, 204 (if no such message from you), 400, 403, 404
    """

    content = await request.json.get('content')
    if not content:
        return error("No content to modify provided", 400)

    try:
        endpoint_id = ObjectId(endpoint_id)
        endpoint = await user.get_endpoint(endpoint_id)

    except bson_errors.InvalidId:
        return error("Invalid endpoint id")

    except ValueError:
        return error("No such endpoint")

    try:
        message_id = ObjectId(message_id)
        message_modified = await endpoint.edit_message(
            user._id, message_id, content
        )

        if message_modified:
            update_message = UpdateMessage(
                {
                    "edited_message": message_id,
                    "new_content": content
                },
                UpdateType.edited_message
            )
            await broadcast_message(endpoint, update_message)
            return success("ok")

        else:
            return success("Nothing to modify", 204)

    except TextEndpoint.exc.NotGroupMember:
        return error("You aren't a group member", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")


@authorized
async def pin_message(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id
    Response: 200, 204 (if no such message), 403, 404
    """

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

        if message_pinned:
            update_message = UpdateMessage(
                {
                    "pinned_message": message_id
                },
                UpdateType.pinned_message
            )
            await broadcast_message(endpoint, update_message)
            return success("ok")

        else:
            return success("Nothing pinned", 204)

    except TextEndpoint.exc.NotGroupMember:
        return error("You aren't a group member", 403)

    except TextEndpoint.exc.NoPermission:
        return error("No permission to pin message", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")


@authorized
async def unpin_message(user: User, endpoint_id: str, message_id: str):
    """
    Requires: endpoint id, message id
    Response: 200, 204 (if no such message), 403, 404
    """

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

        if message_unpinned:
            update_message = UpdateMessage(
                {
                    "unpinned_message": message_id
                },
                UpdateType.unpinned_message
            )
            await broadcast_message(endpoint, update_message)
            return success("ok")

        else:
            return success("Nothing pinned", 204)

    except TextEndpoint.exc.NotGroupMember:
        return error("You aren't a group member", 403)

    except TextEndpoint.exc.NoPermission:
        return error("No permission to unpin message", 403)

    except bson_errors.InvalidId:
        return error("Invalid message id")