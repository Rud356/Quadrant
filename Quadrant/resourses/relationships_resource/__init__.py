from Quadrant.resourses.common_variables import UUID4_REGEX
from Quadrant.resourses.quadrant_app import QuadrantAPIApp
from .blocked import BlockedRelationsHandler, BlockedRelationsPageHandler
from .friends import FriendsRelationsHandler, FriendsRelationsPageHandler
from .incoming_friend_requests import IncomingFriendRequestHandler, IncomingFriendsRequestsPageHandler
from .outgoing_friend_requests import OutgoingFriendRequestHandler, OutgoingFriendsRequestsPageHandler
from .relations import RelationsCheckHandler

relationships_resource = QuadrantAPIApp([
    (r"/api/v1/relations/(?P<with_user_id>%s)" % UUID4_REGEX, RelationsCheckHandler),
    (r"/api/v1/relations/blocked/", BlockedRelationsPageHandler),
    (r"/api/v1/relations/blocked/(?P<blocking_user_id>%s)" % UUID4_REGEX, BlockedRelationsHandler),
    (r"/api/v1/relations/friends/", FriendsRelationsPageHandler),
    (r"/api/v1/relations/friends/(?P<friend_user_id>%s)" % UUID4_REGEX, FriendsRelationsHandler),
    (r"/api/v1/relations/incoming_friend_requests", IncomingFriendsRequestsPageHandler),
    (
        r"/api/v1/relations/incoming_friend_requests/(?P<request_sender_id>%s)" % UUID4_REGEX,
        IncomingFriendRequestHandler
    ),
    (r"/api/v1/relations/outgoing_friend_requests/", OutgoingFriendsRequestsPageHandler),
    (
        r"/api/v1/relations/outgoing_friend_requests/(?P<request_to_id>%s)" % UUID4_REGEX,
        OutgoingFriendRequestHandler
    ),
])

__all__ = ("relationships_resource", )
