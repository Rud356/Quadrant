from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin

spec = APISpec(
    title="Quadrant chat server",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(description="Documentation for Quadrant chat API"),
    plugins=[TornadoPlugin(), MarshmallowPlugin()],
)

spec.components.security_scheme(
    "cookieAuth", {
        "type": "apiKey",
        "in": "cookie",
        "name": "token"
    }
)
spec.components.security_scheme(
    "sessionID", {
        "type": "integer",
        "in": "cookie",
        "name": "session_id"
    }
)
