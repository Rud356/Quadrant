
from data.views import User
from data.crypt import Encryption
from quart import Quart, Response, request, session, jsonify
app = Quart(__name__)
class CChat:
    client_pool = {}
    def __init__(self, port=5000):
        self.port = port

    def run(self):
        try:
            app.run(port=self.port, certfile='cert.pem', keyfile='key.pem')
        except Exception as e:
            app.run(port=self.port)


class Routes:
    @staticmethod
    @app.route("/", ["GET"])
    async def greet():
        return 'hello!'

    @staticmethod
    @app.route()

    @staticmethod
    @app.route("/login/<string:login>", methods=["POST", "PUT"])
    async def auth(login):
        # TODO: add exception of incorrect data
        pwd = str(await request.get_data(), 'utf-8')
        try:
            token = User.auth(login, pwd)
            CChat.client_pool.update(token[1])
            r = Response("Authorized", status=200)
            r.set_cookie("token", token[0], secure=False, path='/')
            return r
        except User.Exceptions.Unauthorized:
            return Response("Incorrect login or password", status=401)

    @staticmethod
    @app.route("/me", methods=["GET"])
    async def me_info():
        token = request.cookies.get("token")
        if token is not None:
            info: User = CChat.client_pool.get(token, None)
            if info is not None:
                return jsonify(**info.__repr__())
        return Response("Not logged in", status=401)

CChat().run()