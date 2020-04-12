# Base api link
/api/v<version>

## User related
/user/login - POST
/user/logout - POST
/user/delete - DELETE

/users/<id> - GET user with id (if is friend or has common groups)
/user/self - GET user himself if logged in
/user/self/dms - GET list of direct messages channels
/user/self/dms/<id> - GET dm with one certain user (image, user, last msg id)
/user/self/groups - GET list of all group dms (title, image, owner, members)