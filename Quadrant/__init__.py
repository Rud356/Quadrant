from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from Quadrant.config import quadrant_config

handlers = []
quadrant_chat = Application(
    handlers,
    cookie_secret=quadrant_config.Security.cookie_secret.value,
    debug=quadrant_config.debug_mode.value,
    xsrf_cookies=True,
)


if quadrant_config.host_static_files_internally.value:
    # Add static files handlers
    pass

http_server = HTTPServer(quadrant_chat, max_header_size=quadrant_config.max_payload_size.value)

if __name__ == "__main__":
    http_server.listen(port=quadrant_config.HttpChatServer.port.value)
    IOLoop.current().start()
