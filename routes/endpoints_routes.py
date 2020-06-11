from time import time
from typing import List

from bson import ObjectId
from bson import errors as bson_errors
from quart import request

from app import app, connected_users
from models.endpoint_model import DMChannel, GroupDM, MetaEndpoint, TextEndpoint
from models.enums import ChannelType, UpdateType
from models.invites_model import Invite
from models.message_model import UpdateMessage
from user_view import User

from .middlewares import authorized, validate_schema
from .responces import error, success
from .schemas import dm_endpoint


async def broadcast_update_message(endpoint: TextEndpoint, message: UpdateMessage):
    members = endpoint.members

    for member_id in members:
        member = connected_users.get(member_id)

        if member is None:
            continue

        await member.add_message(message)


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


@authorized
async def get_endpoints(user: User):
    endpoints: List[ObjectId] = await user.get_endpoints_ids()

    return success(endpoints)


@authorized
async def get_endpoints_dict(user: User):
    endpoints: dict = await user.get_endpoints()

    return success(endpoints)


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


@authorized
async def create_group(user: User, title: str):
    try:
        new_group_dm = await GroupDM.create_endpoint(
            user._id, title
        )

        return success({"endpoint": new_group_dm.__dict__})

    except bson_errors.InvalidId:
        return error("Invalid user with id")

    except ValueError as ve:
        return error(str(ve), 409)


@authorized
async def create_group_invite(user: User, group_id: str):
    try:

        limit = request.args.get('user_limit', -1, int)
        expires = request.args.get('expires_at', round(time() + 60*60), int)

        group_id = ObjectId(group_id)
        endpoint = await MetaEndpoint.get_endpoint(
            user._id, group_id
        )

        if endpoint._type != ChannelType.group:
            return error("It's not an group dm channel")

        invite = endpoint.create_invite(user._id, limit, expires)

        return success(invite)

    except bson_errors.InvalidId:
        return error("Invalid user with id")

    except ValueError as ve:
        return error(str(ve), 403)


@authorized
async def get_invites(user: User, group_id: str):
    try:
        group_id = ObjectId(group_id)
        endpoint = await MetaEndpoint.get_endpoint(user._id, group_id)

        if endpoint._type != ChannelType.group:
            return error("Not an group channel")

        if user._id not in endpoint.members:
            return error("Not a group member")

        invites = await Invite.endpoints_invites(endpoint._id)
        return success(invites)

    except bson_errors.InvalidId:
        return error("Invalid group id", 404)


@authorized
async def delete_invite(user: User, group_id: str, code: str):
    try:
        group_id = ObjectId(group_id)
        endpoint = await MetaEndpoint.get_endpoint(user._id, group_id)

        if endpoint._type != ChannelType.group:
            return error("Not an group channel")

        if user._id != endpoint.owner:
            return error("No permission")

        deleted = await endpoint.delete_invite(code)
        return success(bool(deleted))

    except bson_errors.InvalidId:
        return error("Invalid group id", 404)


@authorized
async def join_group(user: User):
    try:
        code = request.args.get('code', '')
        if not len(code):
            return error("No code given", 400)

        endpoint_id = await GroupDM.accept_invite(user._id, code)
        endpoint = await MetaEndpoint.get_endpoint(user._id, endpoint_id)

        update_message = UpdateMessage(
            {
                "new_group_member": user._id
            },
            UpdateType.new_group_member
        )
        await broadcast_update_message(endpoint, update_message)
        return success(endpoint.__dict__)

    except ValueError:
        return error("Invalid invite code", 400)


@authorized
async def leave_group(user: User, group_id: str):
    try:
        group_id = ObjectId(group_id)
        endpoint = await MetaEndpoint.get_endpoint(user._id, group_id)

        if endpoint.owner == user._id:
            return error("Creator of group can't leave groups", 403)

        await endpoint.remove_user(user._id)

        update_message = UpdateMessage(
            {
                "left_group": user._id
            },
            UpdateType.left_group_member
        )
        await broadcast_update_message(endpoint, update_message)
        return success(endpoint.__dict__)

    except bson_errors.InvalidId:
        return error("Invalid group id", 404)

    except ValueError:
        return error("Invalid group id", 404)


@authorized
async def kick_from_group(user: User, group_id: str, kicked: str):
    try:
        group_id = ObjectId(group_id)
        endpoint = await MetaEndpoint.get_endpoint(user._id, group_id)

        if kicked == user._id:
            return error("You can't kick yourself", 403)

        if endpoint.owner != user._id:
            return error("You don't have permissions to kick", 403)

        if kicked not in endpoint.members:
            return error("No such user in members", 400)

        await endpoint.remove_user(kicked)

        update_message = UpdateMessage(
            {
                "kicked_from_group": kicked
            },
            UpdateType.kicked_group_member
        )
        await broadcast_update_message(endpoint, update_message)
        return success(endpoint.__dict__)

    except bson_errors.InvalidId:
        return error("Invalid user with id")

    except ValueError:
        return error("Invalid id", 400)
