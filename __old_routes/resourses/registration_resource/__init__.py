from __old_routes.resourses.quadrant_app import QuadrantAPIApp
from .registration import InternalRegistrationHandler

registration_resource = QuadrantAPIApp([
    (r"/api/v1/registration/internal", InternalRegistrationHandler),
])

__all__ = ("registration_resource", )