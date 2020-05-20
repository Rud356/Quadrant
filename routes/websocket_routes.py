import json
from app import app
from bson import ObjectId
from asyncio import sleep
from asyncio import CancelledError
from bson import errors as  bson_errors
from quart import websocket, copy_current_websocket_context
from views import UserView

from .middlewares import auth_websocket


async def broadcaster(user: UserView):
    for message in user.message_queue:
        await websocket.send(message)


class WSMessage:
    def __init__(self, user: UserView):
        self._index = -1
        self.user = UserView

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, val: int):
        self.index = val

    async def __call__(self, msg: bytes):
        try:
            await websocket.send(msg)

        except CancelledError:
            self.user.to_clear_connections.append(self.index)


@app.websocket('/api/ws')
@auth_websocket
async def add_websocket(user: UserView):
    new_ws = WSMessage(user)
    user_ws = copy_current_websocket_context(new_ws)
    await websocket.send(b'{"responce":"Authorized!"}')
    await user.add_ws(user_ws)
