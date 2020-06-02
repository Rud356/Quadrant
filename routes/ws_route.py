from asyncio import CancelledError, sleep

from quart import copy_current_websocket_context, websocket

from app import app
from views import User

from .middlewares import auth_websocket


class WebsocketNotifier:
    def __init__(self, user: User):
        self.user = user
        self.message_pool = []

    async def __call__(self):
        while True:
            try:
                message_pool_length = len(self.message_pool)

                for _ in range(message_pool_length):
                    message = self.message_pool.pop(0)
                    await websocket.send(str(message))

                await sleep(0.1)

            except CancelledError:
                break

        # Deleting websocket from pool
        self.user.connected.remove(self)


@app.websocket('/api/ws')
@auth_websocket
async def add_websocket(user: User):
    """
    Payload: json
    {
        "token": "string token"
    }
    Response: Authorized, 401
    """
    new_ws_user = WebsocketNotifier(user)
    new_ws_user = copy_current_websocket_context(new_ws_user)
    await websocket.send("Authorized!")
    await user.add_ws(new_ws_user)
