# Listing of endpoints

All methods can return these statuse codes: 200 400 401 403 404  
405 being returned by validator of api version  
All fine requests returning information as json where returned data is in filed - responce  
Websockets sending first greeting message and then only used for resending back new messages  

## TODOS:
Add more endpoints  
Add invites routes  
Add file server and ui + api wrapper  
Add route to get pinned messages  
Add route to get messages after specific  
Resend updates to users (nicknames, endpoints properties, message properties (exampl: pinned, edited, deleted))  

| endpoint | method | required as json | description |
| :--- | :---: | :---: | :--- |
| /api/users/login | POST | login: str, password: str | logging in as normal user and getting in return user object as json |
| /api/users/reistrate | POST | nick: str, bot: bool, parent: str OR login + password | registrates new user |
| /api/users/me/logout | GET | none | logs out you from account |
| /api/users/me | GET | none | returns yourself as json representation (image can be gotten over your id) |
| /api/me/nick?new_nick=<string:new_nick> | POST | none | setting new nickname for user |
| /api/me/friendcode?code=<string:your_friendcode> | POST | none | setting new friend code for user |
| /api/me/text_status | POST | text_status: str | setting text status of user |
| /api/me/status/<int:new_status> | POST | none | setting status of user |
| /api/users/<string:id> | GET | none | returns user representation as json |
| /api/friends | GET | none | returns all friends json representation as json |
| /api/friends?code=<string:friendcode> | POST | none | sends friend request to user with this friendcode |
| /api/friends/<string:id> | POST | none | sends friend request to user with setted id |
| /api/friend_requests | GET | none | returns all friends requests made by you |
| /api/pending_requests | GET | none | returns all incoming to you friend requests |
| /api/friend_requests/<string:id> | DELETE | none | cancels sent friend request |
| /api/pending_requests/<string:id> | POST | none | respond to friend request by accepting it |
| /api/pending_requests/<string:id>?accept=False | POST | none | respond to friend request by denying it |
| /api/blocked | GET | none | returns all users blocked by you |
| /api/blocked/<string:id> | POST | none | can throw code 204 if user is already blocked, if not - adding to blocked |
| /api/endpoints | GET | none | returns all small endpoints (dms, groputs) as json |
| /api/endpoints/<string:endpoint_id> | GET | none | returns specific endpoint |
| /api/endpoints/create_endpoint?=dm | POST | with: str (another user id) | creates new endpoint for users |
| /api/endpoints/<string:endpoint_id>/messages | GET | none | returns 100 fresh messages |
| /api/endpoints/<string:endpoint_id>/messages/from/<string:message_id> | GET | none | returns 100 mesages that was before one with given id |
| /api/endpoints/<string:endpoint_id>/messages/<string:message_id> | GET | none | returns exact message |
| /api/endpoints/<string:endpoint_id>/messages/<string:message_id> | PATCH | content: str | editing message from you |
| /api/endpoints/<string:endpoint_id>/messages/<string:message_id>/pin?=<True or False> | PATCH | none | editing message from you |
| /api/endpoints/<string:endpoint_id>/messages | POST | content: str (must be) | posting new message to endpoint (more details later) |
| /api/endpoints/<string:endpoint_id>/messages/<string:message_id> | DELETE | none | deleting your message |
| /api/endpoints/<string:endpoint_id>/messages/<string:message_id>?force=True | DELETE | none | trying to delete others message (checks permissions) |
| /api/ws/add | WebSocket | token: str | adding your websocket to your user and letting you catch messages and updates in real time |
