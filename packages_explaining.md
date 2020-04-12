# This is explanation of all packages

Notes:
1. With `?` will be marked incoming package
2. With `!` responce package
3. Optional fields will be marked with `*` before them in json strings
### User related packages

 ? Authorization package
 ```json
 {
    "login": "some_login_of_user",
    "password": "some_password",
    "*DoubleAuth": "secCode"
 }
 ```
 ! Possible responces
 200 - Success (giving a cookie with token for this user)\
  ```json
  {
      "name": "username",
      "relationships": [], // relationships with different users
      "status": 1,
      "*status_text": "example",
      "servers": [],
      "dms": [], // maybe will change later
      "group_dms": [],
      "*is_bot": false, // indicates if user is bot
      "*created_by": 123, // users id who owns a bot
      "created_at": 123 // time user was created
  }
  ```
 400 - Bad request (if some field isn't given)\
 401 - Unauthorized (incorrect password or login)\
 429 - Too much requests on login (if user spamming login)\

 ? Token auth
 ```json
 {
     "token": "64 or more random chars" //hex symbols
 }
 ```
 Same as standart login

 ? Logout
 Token being taken from cookie\
 ! Responces
 202 - Logging out\
 401 - Unauthorized\

 ? Change nickname
 taking user from token\
 ```json
 {
     "new_nickname": "nickname_upd", // not longer than 50 chars
     "*DoubleAuth": "secCode"
 }
 ```
 ! Responces
 200 - everything is fine (send update to those who have to see maybe?)\
 401 - unauthorized\

 ? Set status
 ```json
 {
     "status": 0, // can be other values, will be in code
     "*custom_text": "maybe some text around 100 chars"
 }
 ```
 ! Responces
 200 - fine\
 401 - unauthorized\

 ? Friend request
 Sending to user defined in url\
 ! Responce
 200 - file, waiting users responce\
 401 - unauthorized\
 403 - user not accepting friends without incommon friends or chats\
 403 - was blocked by accepting side\

 ? Responding to friends request
 Getting user to who's responce we answering from url\
 ```json
 {
     "responce": 1 // define codes in code :^)
 }
 ```
 ! Responce
 200 - fine\
 401 - unauthorized\

 ? Cancel responce
 Getting user who cancels from token and for whom\
 ! Responce
 200 - fine\
 401 - unauthorized\
 403 - already accepted\

 ? Deleting
 Getting user from cookies\
 ! Responce
 202 - accepted\
 401 - unauthorized\

 ? Change login\
 ```json
 {
     "new_login": "upd_login", // maybe hashed?
     "*DoublAuth": "secCode"
 }
 ```
 ! Responce
 200 - fine (throwing user from acc away to make him relogin)\
 401 - unauthorized\

 ? Change password\
 ```json
 {
     "new_password": "upd_pwd", // hash maybe?
     "*DoublAuth": "secCode"
 }
 ```
 ! Responce
 200 - fine (throwing user from acc away to make him relogin)\
 401 - unauthorized\

### DMs
 These can be only created with friends or users that in common channels
 ? Taking user with whom we create chat from link or go to channe;\
 ! Responce\
 200 - fine\
 ```json
 {
     "dm_with": 1234, // users id
     "last_message_id": 123,
     "notification_state": 1 // define in code
 }
 ```
 401 - unauthorized\
 403 - already exists\
 403 - blocked\

### Group dms
 These existing as a group for up to 25 persons in chat\
 Can make voice calls and stuff together\
 Also can set inviting mode: `owner only` or `all members`\


 ? create channel\
 ```json
 {
     "*chat_title": "some_name", // can be used default title
     "*invitation_mode": 0, // owner only by default but can be changed
     "members": [], // list of members
     "member_count": 1, // owner only, if 0 - destroy chat
     "owner_id": 123,
     "*nsfw": false // by default - false
 }
 ```\

 ! Responce group_dm object
 200 - fine\
 ```json
 {
     "chat_title": "title",
     "owner_id": 123,
     "members": [], // users owner
     "member_count": 1,
     "nsfw": false,
     "last_message_id": 1, // whatever
 }
 ```
 (maybe add pinning channels for specific users?)
 401 - unauthorized\


 ? create invite\
 Taking invite creator from token and looking at least if he can make an invite
 ```json
 {
     "group_id": 123,
     "limit": 1, // how a lot of users can use this invite before its gone
     "time_limit": 60 // how long in minutes it will live
 }
 ```
 ! Invite responce
 200 - invite created (giving internal invite link)\
 401 - unauthorized\
 403 - can't create invite links\


 ? pin message

 Pinning message if member is existing there
 Taking user that pins message from cookies

 ! responce\
 200 - message pinned\
 401 - unauthorized\

 ? use invite link
 Taking user from cookie and adding to related chat\

 ! Responce
 200 - added to group\
 401 - unauthorized\
 403 - expired\