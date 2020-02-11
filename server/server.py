from quart import Quart, Response, request
from data.views import User
app = Quart(__name__)
class CChat:
    client_pool = {}
    def __init__(self, port=5000):
        self.port = port

    def run(self):
        app.run(port=self.port)

class Routes:
    @staticmethod
    @app.route("/", ["GET"])
    async def greet():
        return 'hello!'

    @staticmethod
    @app.route("/login/<string:login>", methods=["POST", "PUT"])
    async def auth(login):
        pwd = str(await request.get_data(), 'utf-8')
        try:
            token = User.auth(login, pwd)
            CChat.client_pool.update(token)
            r = Response("12345", status=200)
            r.set_cookie("token", "1234556")
            return r
        except User.Exceptions.Unauthorized:
            return Response("Incorrect login or password", status=401)

CChat().run()