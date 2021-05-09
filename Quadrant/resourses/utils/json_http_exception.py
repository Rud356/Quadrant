from tornado.web import HTTPError
from tornado import httputil

from .json_wrapper import JsonWrapper


class JsonHTTPError(HTTPError):
    def __str__(self):
        message = JsonWrapper.dumps({
            "status_code": self.status_code,
            "reason": self.reason or httputil.responses.get(self.status_code, "Unknown"),
        })
        return message
