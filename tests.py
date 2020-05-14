from models import *
from bson import ObjectId
import asyncio

async def main():
    print("begin")
    # new_user = await User.create_user("Test1", login="hello_bbbbbbbbb12", password="World_bbbbbbbbb12")
    again_user = await User.from_id(ObjectId("5ebc94ce1bdfedd14ac4697b"))
    second_user = await User.from_id(ObjectId("5ebc96259747cbb58cc6b2f1"))
    # await second_user.send_friend_request(again_user._id)
    print(again_user.pendings_incoming)
    # await again_user.unblock_user(second_user._id)
    # await again_user.responce_friend_request(second_user._id)
    dm = await DMchannel.create_endpoint(again_user._id, second_user._id)
    await dm.send_message(again_user._id, "Hello world!!!!")
    print(again_user)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())