from models import *
from bson import ObjectId
import os
import asyncio

os.system('cls')

async def main():
    print("begin")
    user = await User.authorize('hello_bbbbbbbbb12', 'World_bbbbbbbbb12')
    chats = await user.small_endpoints()

    dm = chats[0]
    await dm.send_message(user._id, "Sorting test")
    await dm.send_message(user._id, "Lets see how it works")
    message = await dm.send_message(user._id, "Testing again")
    print("from message: ", message._id)
    messages_list = await dm.get_messages(user._id, message._id)

    for msg in messages_list:
        print(msg)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())