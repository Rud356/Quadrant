from Quadrant.resourses.quadrant_app import QuadrantAPIApp
from .authorization import InternalAuthorizationHandler

authorization_resource = QuadrantAPIApp([
    # TODO: add oauth (maybe) and bots authorization
    (r"/api/v1/authorization/internal", InternalAuthorizationHandler),
])