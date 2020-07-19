from asyncio import CancelledError, sleep, ensure_future

from quart import copy_current_websocket_context, websocket

from app import app
from user_view import User

from .middlewares import auth_websocket


class WebsocketNotifier:
    def __init__(self, user: User):
        self.user = user

    async def __call__(self):
        while True:
            try:
                print("Started gen")
                message = yield
                print("Putted val", message)

                if message:
                    await websocket.send(str(message))
                    print('Sent')

            except CancelledError:
                break

        # Deleting websocket from pool
        current_ws_index = self.user.connected.index(self)
        self.user.kill_websockets.append(current_ws_index)


@app.websocket('/api/ws')
@auth_websocket
async def add_websocket(user: User):
    # TODO: change logic to make this more usable
    """
    Payload: json
    {
        "token": "string token"
    }
    Response: Authorized, 401
    """

    new_ws_user = WebsocketNotifier(user)
    new_ws_user = copy_current_websocket_context(
        new_ws_user
    )

    await websocket.send("Authorized!")
    await user.add_ws(new_ws_user)
