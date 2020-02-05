from quart import Quart, websocket

app = Quart(__name__)

@app.route('/')
async def give_ui():
    return "testing"


app.run()
