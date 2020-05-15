from models import *
from bson import ObjectId
import asyncio

async def main():
    print("begin")
    _id = await User.friendcodes_owner("hello_world")
    user = await User.from_id(_id)
    print(_id)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())