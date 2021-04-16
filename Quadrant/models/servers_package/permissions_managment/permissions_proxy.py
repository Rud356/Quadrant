from typing import List, TYPE_CHECKING, Union

from .channels_overwrites import RolesOverwrites, UsersOverwrites
from .permissions import PermissionsSet, TextChannelPermissions
from .roles import ServerRole

if TYPE_CHECKING:
    from Quadrant.models.servers_package.server_member import ServerMember
    from Quadrant.models.servers_package.server_channel import ServerChannel


class TextChannelsPermissionsProxy:
    def __init__(self, member: ServerMember, text_channel: ServerChannel, session):
        self.member = member
        self.text_channel = text_channel
        self.server_id = member.server_id

        self.session = session

    async def get_permissions(self) -> Union[PermissionsSet, TextChannelPermissions]:
        """
        Looking up for users_package permissions in order:
        Is user admin?
        Does user have any overwrites on that channel?
        First found overwrite for role from those that user has (ordered by roles position).
        Default permissions.

        :return: permissions set (has all fields of TextChannelPermissions).
        """
        default_permission = self.text_channel.permissions
        roles: List[ServerRole] = self.member.roles

        roles_ids = []
        for role in roles:
            # Looking for administrator permission since it's one of the most powerful
            if role.permissions.administrator:
                return role.permissions

            roles_ids.append(role.role_id)

        users_overwrites = await UsersOverwrites.get_overwrites_for_channel(
            self.server_id, self.text_channel.id, self.member.id, session=self.session
        )

        if users_overwrites:
            return users_overwrites

        permissions: PermissionsSet = await RolesOverwrites.get_permissions_overwrites_by_roles(
            self.server_id, self.text_channel.channel_id, roles_ids, session=self.session
        )

        if not permissions:
            return default_permission

        else:
            return permissions
