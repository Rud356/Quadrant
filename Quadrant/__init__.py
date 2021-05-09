from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from Quadrant.config import quadrant_config
from Quadrant.resourses import router

http_server = HTTPServer(router)
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

with open(quadrant_config.static_folder_location.value / "swagger.yml") as f:
    f.write(spec.to_yaml())

if quadrant_config.host_static_files_internally.value:
    # Add static files handlers
    pass

if __name__ == "__main__":
    http_server.listen(port=quadrant_config.HttpChatServer.port.value)
    IOLoop.current().start()
