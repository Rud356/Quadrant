from quart import Quart, Response, request, session, jsonify

app = Quart(__name__)


class CChat:
    __slots__ = "port", "host", "mongo_conn", "debug"
    def __init__(self, host='localhost', port=5000, debug=False):
        self.port = port
        self.host = host
        self.debug = debug

    def run(self):
        if self.debug:
            app.run('localhost', self.port, True)
        else:
            app.run(self.host, self.port, False)


class Routes:


    class Authorization:
        @staticmethod
        @app.route("/reg", methods=["POST"])
        async def create_user():
            pass

        @staticmethod
        @app.route("/login", methods=["POST"])
        async def auth():
            #the splitter will be space just cuz i wanna to
            auth_data = await request.get_data()
            try:
                auth_data = str(auth_data, 'utf-8')
                #TODO: replace with actual logging in
                return Response("true")
            except TypeError:
                return Response("Incorrect data", status=501)

        @staticmethod
        @app.route("/logout", methods=["DELETE"])
        async def logout_client():
            #TODO: add destroying server
            return Response("will do later", status=202)


    class User:
        @staticmethod
        @app.route("/self", methods=["GET"])
        async def self_user_repr():
            #TODO: replace with real responce dependant from token
            return Response("Fine")

        @staticmethod
        @app.route("/self", methods=["PATCH", "PUT"])
        async def modify_self():
            pass

        @staticmethod
        @app.route("/user/<int:id>")
        async def get_user(id):
            pass


        class FriendsManagment:
            @staticmethod
            @app.route("/self/friends", methods=["GET"])
            async def get_friends():
                pass

            @staticmethod
            @app.route("/self/friends", methods=["PUT"])
            async def add_friends():
                pass

            @staticmethod
            @app.route("/self/friends", methods=["DELETE"])
            async def remove_friends():
                pass


        class BlockedManagment:
            @staticmethod
            @app.route("/self/blocked", methods=["GET"])
            async def get_blocks():
                pass

            @staticmethod
            @app.route("/self/blocked", methods=["PUT"])
            async def add_blocked():
                pass

            @staticmethod
            @app.route("/self/blocked", methods=["DELETE"])
            async def unblock():
                pass


        class DMManagment:
            @staticmethod
            @app.route("/self/dm", methods=["GET"])
            async def get_dm_channels():
                pass

            @staticmethod
            @app.route("/self/dm", methods=["POST"])
            async def start_dm():
                pass

            @staticmethod
            @app.route("/self/dm", methods=["DELETE"])
            async def destroy_dm():
                pass

    class Channel:


CChat(debug=True).run()