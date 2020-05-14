from models import *
from bson import ObjectId
import asyncio

async def main():
    print("begin")
    again_user = await User.from_id(ObjectId('5ebd4f341d4cd5908f3d192e'))
    second_user = await User.from_id(ObjectId('5ebd4f331d4cd5908f3d192d'))
    # await second_user.responce_friend_request(again_user._id)
    # print(again_user.pendings_incoming)
    # await again_user.unblock_user(second_user._id)
    # dm = await DMchannel.create_endpoint(again_user._id, second_user._id)
    # await dm.send_message(again_user._id, "Hello world!!!!")
    dms = await second_user.small_endpoints()
    await dms[0].send_message(again_user._id, "Hello world again!")
    print(dms)
    print(second_user)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())