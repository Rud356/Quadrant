from asyncio import CancelledError, sleep, Queue

from quart import copy_current_websocket_context, websocket

from app import app
from user_view import User

from .middlewares import auth_websocket


class WebsocketNotifier:
    def __init__(self, user: User):
        self.user = user
        self.can_enqueue = True
        self.message_queue = Queue()

    def clear_queue(self):
        for _ in range(self.message_queue.qsize()):
            self.message_queue.get_nowait()
            self.message_queue.task_done()

    async def enqueue(self, message):
        if self.can_enqueue:
            await self.message_queue.put(message)

    async def run(self):
        run = True

        while run:

            while not self.message_queue.empty():
                try:
                    message = await self.message_queue.get()
                    await websocket.send(str(message))

                except CancelledError:
                    self.can_enqueue = False
                    run = False
                    break

            else:
                await sleep(0.1)

        # Deleting websocket from pool
        self.clear_queue()
        self.user.kill_websockets.append(self)


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

    user_ws = WebsocketNotifier(user)
    user_ws.run = copy_current_websocket_context(
        user_ws.run
    )

    await user.add_ws(user_ws)
    await websocket.send("Authorized")
    await user_ws.run()
