from __old_routes.resourses.quadrant_app import QuadrantAPIApp
from .sessions import (
    UsersAllSessionsTerminationHandler, UsersCurrentSessionHandler,
    UsersExactSessionHandler, UsersSessionsHistoryHandler
)

sessions_resource_app = QuadrantAPIApp([
    (r"/api/v1/sessions/", UsersSessionsHistoryHandler),
    (r"/api/v1/sessions/current", UsersCurrentSessionHandler),
    (r"/api/v1/sessions/(?P<session_id>\d+)", UsersExactSessionHandler),
    (r"/api/v1/sessions/all", UsersAllSessionsTerminationHandler),
])

__all__ = ("sessions_resource_app", )
