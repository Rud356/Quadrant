from Quadrant.resourses.common_variables import UUID4_REGEX
from Quadrant.resourses.quadrant_app import QuadrantAPIApp
from .profile_managment import (
    AboutMeHandler, ProfilePictureHandler, UserStatusHandler,
    UserTextStatusHandler, UsernameHandler
)
from .users import UserResourceHandler

users_resource_app = QuadrantAPIApp([
    # TODO: add partial user profile fetching maybe?
    # User details
    (r"/api/v1/users/(?P<user_id>%s)" % UUID4_REGEX, UserResourceHandler),
    # Profile management
    (r"/api/v1/users/me", AboutMeHandler),
    (r"/api/v1/users/me/status", UserStatusHandler),
    (r"/api/v1/users/me/text_status", UserTextStatusHandler),
    (r"/api/v1/users/me/username", UsernameHandler),
    (r"/api/v1/users/me/profile_picture", ProfilePictureHandler),
])

__all__ = ("users_resource_app", )
