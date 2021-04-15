from sqlalchemy import Boolean, Column, ForeignKey

from Quadrant.models.db_init import Base


class PermissionsSet(Base):
    administrator = Column(Boolean, default=False)
    manage_server = Column(Boolean, default=False)
    manage_roles = Column(Boolean, default=False)
    manage_channels = Column(Boolean, default=False)
    pin_messages = Column(Boolean, default=False)
    deaf_others = Column(Boolean, default=False)
    mute_others = Column(Boolean, default=False)
    delete_others_messages = Column(Boolean, default=False)
    delete_messages = Column(Boolean, default=False)
    use_bots = Column(Boolean, default=False)
    send_links = Column(Boolean, default=True)
    attach_files = Column(Boolean, default=True)
    speak_in_voice_channel = Column(Boolean, default=True)
    connect_to_voice_channel = Column(Boolean, default=True)
    write_messages = Column(Boolean, default=True)
    react_on_message = Column(Boolean, default=True)
    read_messages = Column(Boolean, default=True)

    __abstract__ = True


class TextChannelPermissions:
    channel_id = Column(ForeignKey("server_channels.channel_id"), primary_key=True)
    manage_channels = Column(Boolean, default=False)
    pin_messages = Column(Boolean, default=False)
    delete_others_messages = Column(Boolean, default=False)
    delete_messages = Column(Boolean, default=False)
    use_bots = Column(Boolean, default=False)
    send_links = Column(Boolean, default=True)
    attach_files = Column(Boolean, default=True)
    write_messages = Column(Boolean, default=True)
    react_on_message = Column(Boolean, default=True)
    read_messages = Column(Boolean, default=True)


class RolesPermissions(PermissionsSet):
    role_id = Column(ForeignKey("server_roles.id"), primary_key=True)
    __tablename__ = "roles_default_permissions"


class RolesPermissionsOverwrites(PermissionsSet):
    overwrite_id = Column(ForeignKey("roles_server_permissions_overwrites.overwrite_id"), primary_key=True)
    __tablename__ = "roles_overwritten_permissions"


class UsersPermissionsOverwrites(PermissionsSet):
    overwrite_id = Column(ForeignKey("users_server_permissions_overwrites.overwrite_id"), primary_key=True)
    __tablename__ = "users_overwritten_permissions"
