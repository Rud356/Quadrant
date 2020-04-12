# Base api link
/api/v<version>

## Routes
/user/login - POST\
/user/logout - POST\
/user/reset - POSt\
/user/delete - DELETE\

/user/<id> - GET user with id (if is friend or has common groups)\
/user/<id> - POST friends request (check on if it was already sent or user sender is blocked)\
/user/<id>/cancel - POST cancels friends request\
/user/*/image - GET image of user (only if has common groups, are freinds or self)\

/user/self - GET user himself if logged in\
/user/self - PATCH users information\

/user/self/pendings - GET all friends requests\
/user/self/pendings/<id> - POST responce to pending\

/user/self/friends - GET all friends\
/user/self/friends/<id> - GET info about one friend\
/user/self/friends/<id> - DELETE one friend\

/user/<id>/add_blocked - POST new blocked\
/user/self/blocked - GET all blocked\
/user/self/blocked/<id> - DELETE blocked user from list\

/user/self/image - PATCH image update\

/user/self/dms - GET list of direct messages channels\
/user/self/dms/<id> - GET dm with one certain user (image, user, last msg id)\
/user/self/dms/<id>/messages - GET last 100 messages (or from given id as json param)\
/user/self/dms/<id>/messages - POST new message to db (if not blocked and friend)\
/user/self/dms/<id>/messages/<id> - PATCH sent message (can be pin status for anyone and edit for own messages)\
/user/self/dms/<id>/messages/<id> - DELETE own message\


/user/self/groups - GET list of all group dms (title, image, owner, members)\
/user/self/groups/<id> - GET info about one group\
/user/self/groups/<id>/create_invite - POST a new invite with params and get link\
/groups/<id>/<code> - accept invite\
/user/self/groups/<id>/messages - GET last 100 messages (or from given id as json param)\
/user/self/groups/<id>/messages - POST new message\
/user/self/groups/<id>/messages/<id> - PATCH edit message (if own message or pin message)\
/user/self/groups/<id>/messages/<id> - DELETE message (own msg, or if deleter is owner of group)\

> all server modifications and accesses should be checked before doing anything\
/user/self/servers - GET servers list\
/user/self/servers/<id> - GET one server\
/user/self/servers/<id> - PATCH information about server (if have permissions)\
/user/self/servers/<id> - DELETE (if is owner)\

/user/self/servers/<id>/create_invite - POST a new invite creation request and get invite link with params in payload\
/server/<id>/<code> - GET acception of invite\

/user/self/servers/<id>/<channel_id> - GET one channel\
/user/self/servers/<id>/<channel_id> - PATCH information about channel\
/user/self/servers/<id>/<channel_id> - DELETE channel\

/user/self/servers/<id>/<channel_id>/messages - GET last 100 messages (or from given id as json param)\
/user/self/servers/<id>/<channel_id>/messages - POST a new message (by default around 2.5k symbols)\
/user/self/servers/<id>/<channel_id>/messages/<id> - PATCH existing message\
/user/self/servers/<id>/<channel_id>/messages/<id> - DELETE existing message\
/user/self/servers/<id>/<channel_id>/messages/<id>/add_reaction - POST reaction on message\

/user/self/servers/<id>/roles - GET all roles\
/user/self/servers/<id>/roles - POST role object (if have permissions)\
/user/self/servers/<id>/roles/<id> - GET role\
/user/self/servers/<id>/roles/<id> - PATCH role\
/user/self/servers/<id>/roles/<id> - DELETE role\

/user/self/servers/<id>/emojis - GET all emojis\
/user/self/servers/<id>/emojis/<id> - GET emoji\
/user/self/servers/<id>/emojis - POST a new emoji\
/user/self/servers/<id>/emojis - PATCH existing emoji\
/user/self/servers/<id>/emojis - DELETE existing emoji\