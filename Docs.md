# Routes
| route | method |
| ----- | ------ |
| /api/user/login | POST |
| /api/user/logout | GET POST DELETE |
| /api/user/register | POST |
| /api/user/<user_id> | GET |
| /api/user/me | GET |
| /api/me/nick?new_nick=<new_nick> | POST |
| /api/me/friend_code?=code<new_code> | POST |
| /api/me/status/<new_status>| POST |
| /api/me/test_status | POST |
| /api/friends | GET |
| /api/outgoing_requests | GET |
| /api/incoming_requests | GET |
<<<<<<< HEAD
| /api/friends/<user_id> | POST |
| /api/friends/<user_id> | DELETE |
| /api/friends/request?code=<friendcode> | POST |
| /api/incoming_requests/<user_id>?accept=<bool> | POST |
| /api/outgoing_requests/<user_id> | DELETE |
| /api/blocked | GET |
| /api/blocked/<user_id> | POST |
| /api/blocked/<user_id> | DELETE |
| ----- | ------ |
=======
| /api/friends/<<user_id>> | POST |
| /api/friends/<<user_id>> | DELETE |
| /api/friends/request?code=<<friendcode>> | POST |
| /api/incoming_requests/<<user_id>>?accept=<<Bool>> | POST |
| /api/outgoing_requests/<<user_id>> | DELETE |
| /api/blocked | GET |
| /api/blocked/<<user_id>> | POST |
| /api/blocked/<<user_id>> | DELETE |
>>>>>>> 37813c51e0b769de14a33fd72a720ebac8c71546
| /api/endpoints | GET |
| /api/endpoints/<endpoint_id> | GET |
| /api/endpoints/create_endpoint/dm | POST |
<<<<<<< HEAD
| ----- | ------ |
| /api/endpoints/<endpoint_id>/messages | GET POST |
| /api/endpoints/<endpoint_id>/messages/<message_id> | GET DELETE PATCH |
| /api/endpoints/<endpoint_id>/messages/<message_id>?force=True | DELETE |
| /api/endpoints/<endpoint_id>/messages/<message_id>/from | GET |
| /api/endpoints/<endpoint_id>/messages/<message_id>/after | GET |
| /api/endpoints/<endpoint_id>/messages/pinned | GET |
| /api/endpoints/<endpoint_id>/messages/<message_id>/pinned/from | GET |
| /api/endpoints/<endpoint_id>/messages/<message_id>/pinned/after | GET |
| /api/endpoints/<endpoint_id>/messages/<message_id>/pin | PATCH |
| /api/endpoints/<endpoint_id>/messages/<message_id>/unpin | PATCH |
| ----- | ------ |
=======
| /api/endpoints/<<endpoint_id>>/messages | GET POST |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>> | GET DELETE PATCH |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>?force=True | DELETE |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>/from | GET |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>/after | GET |
| /api/endpoints/<<endpoint_id>>/messages/pinned | GET |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>/pinned/from | GET |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>/pinned/after | GET |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>/pin | PATCH |
| /api/endpoints/<<endpoint_id>>/messages/<<message_id>>/unpin | PATCH |
>>>>>>> 37813c51e0b769de14a33fd72a720ebac8c71546
| /api/ws | WebSocket |
| /api/user/set_image | POST |
| /api/user/<user_id>/profile_pic | GET |
| /api/files/upload | POST |
| /api/files/<file_id> | GET |

# Packages
/api/user/login
```json
{
    "login": "hash string",
    "password": "hash password string"
}
```

/api/user/register
```json
{
    "nick": "string",
    "login": "login hash",
    "password": "password hash"
}


/api/me/test_status
```json
{
    "text_status": "Some string"
}```
Max length is 256 symbols

/api/endpoints/create_endpoint/dm
```json
{
    "with": "user id"
}```

/api/endpoints/<string:endpoint_id>/messages POST
```json
{
    "content": "String",
    "files": ["file_id", "file_id2", "..."]
}```

/api/endpoints/<endpoint_id>/messages/<message_id> PATCH
 This is about editing message content
```json
{
    "content": "New content string"
}
```

Websocket connecting
First package should be
```json
{
    "token": "your token"
}
