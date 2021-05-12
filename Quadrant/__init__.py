from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.netutil import Resolver

from Quadrant.config import quadrant_config
from Quadrant.resourses import router

http_server = HTTPServer(router)


if quadrant_config.host_static_files_internally.value:
    # Add static files handlers
    pass

if __name__ == "__main__":
    Resolver.configure("tornado.platform.caresresolver.CaresResolver")
    http_server.listen(port=quadrant_config.HttpChatServer.port.value)
    IOLoop.current().start()
