**Welcome to asyncio_chat repo!**
This project is created to be client and server side solution at the same time
Also this project trying to use as less dependencies as possible

**Current tasks**
[ ] make server functional
[ ] create basic database interaction
[ ] write user auth system workable
[ ] create server api file with everything it needs to run
[ ] make user class to work with everyone connected to server
[ ] add encryption mechanisms to make this crap secure

**Dependencies**
1. peewee
2. pycryptodome

**project structure**
server.py
client.py (not existing yet)
- server_files
    - api_server.py
    - database.py
    - db.db // database itself

*Note: all params marked with ? are optional*
**Relationships and objects**

* package - all raw packages from users
- header - the size of incoming package (default size is 4 bytes)
- pkg_type - type of package we sending
- *other - package specified keywords in json

* message - represents the message from somewhere
Containts fields:
- ID (int)
- Author (int)
- Content (string)
- Attachments (list of ids reffering to attachments)
- Endpoint (id of endpoint channel)
- Timestamp (int)
- Mentions (list of mentions that can be separated onto mentions types)
- pinned (bool)
Default max content length is 2000 chars

* channel - represents any channel with one or more users in
- ID (int)
- Type (int)
- Recievers (list of recievers)
- Banned (list of user ids)
- Roles? (list of ids) - inheriting from the server if it's a part of one
- Roles overwrites?
- nsfw (bool)

* server - represents collection of channels
- ID (int)
- Name (string)
- Icon (int) - the id of saved image
- Owner (int) - it of most previliged user
- Roles? (list of ids) - all roles existing in this server
- Created at (int)
- Channels (list of ints)
- Users (list of ints)

* permissions (int) - represents a permissions user has (inheriting all roles permissions)
bits permissions order
1 - read messages
2 - write messages
3 - manage messages (delete, pin)
4 - add attachments

* users - represents a client that connected to our online server
- ID (int)
- Bans (list of ints) - users id same time being a channel
- Nick (string)
- Discriminator - if user nickname already in use
- Avatar (int) - the id of avatar
- Bot (bool)
- Keypair (keypair) - this object helps us to encrypt/decrypt messages
- Friendlist (list of ints)