from typing import List, TYPE_CHECKING, Union

from .channels_overwrites import RolesOverwrites, UsersOverwrites
from .permissions import PermissionsSet, TextChannelPermissions
from .roles import ServerRole

if TYPE_CHECKING:
    from Quadrant.models.servers.members import ServerMember
    from Quadrant.models.servers.channels import ServerChannel


class ChannelsPermissionsProxy:
    def __init__(self, member: ServerMember, channel: ServerChannel, session):
        self.member = member
        self.channel = channel
        self.server_id = member.server_id

        self.session = session

    async def get_permissions(self) -> Union[PermissionsSet, TextChannelPermissions]:
        default_permission = self.channel.permissions
        roles: List[ServerRole] = self.member.roles
        users_overwrites = await UsersOverwrites.get_overwrites_for_channel(
            self.server_id, self.channel.id, self.member.id, session=self.session
        )

        if users_overwrites:
            return users_overwrites

        roles_ids = []
        for role in roles:
            # Looking for administrator permission since it's one of the most powerful
            if role.permissions.administrator:
                return role.permissions

            roles_ids.append(role.role_id)

        permissions: PermissionsSet = await RolesOverwrites.get_permissions_overwrites_by_roles(
            self.server_id, self.channel.channel_id, roles_ids, session=self.session
        )

        if not permissions:
            return default_permission

        else:
            return permissions
