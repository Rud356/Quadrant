# Routes

This API is based on json format

## Fine requests

All fine requests response can be found inside of `response` field

Later will be added info about what websockets responses you should await

204 in context of app isn't an error so you should not count it as one too

## Errors

All fails will tell you a bit more about what happened in `description` field

## [Bot_managment](/docs/Bot_managment.md)

| route | method |
| ----- | ------ |
| /api/bots | GET |
| /api/bots/registrate | POST |
| /api/bots/<bot_id\>/<nick\> | POST |
| /api/bots/<bot_id\>/update_token | POST |
| /api/bots/<bot_id\> | DELETE |

## [User_routes](/docs/User_routes.md)

| route | method |
| ----- | ------ |
| /api/user/login | POST |
| /api/user/logout | POST GET DELETE |
| /api/user/register | POST |
| /api/user/<id\> | GET |
| /api/user/me | GET |
| /api/user/me | DELETE |
| /api/user/keep-alive | GET |
| /api/user/update_token | POST |
| /api/me/update | POST |

## [Relations_routes](/docs/Relations_routes.md)

| route | method |
| ----- | ------ |
| /api/friends/<int:page\> | GET |
| /api/blocked/<int:page\> | GET |
| /api/incoming_requests/<int:page\> | GET |
| /api/outgoing_requests/<int:page\> | GET |
| /api/outgoing_requests/<id\> | DELETE |
| /api/incoming_requests/<id\> | POST |
| /api/friends/<id\> | POST |
| /api/friends/request | POST |
| /api/friends/<id\> | DELETE |
| /api/blocked/<id\> | POST |
| /api/blocked/<id\> | DELETE |

## [Endpoint_routes](docs/Endpoint_routes.md)

| route | method |
| ----- | ------ |
| /api/endpoints | GET |
| /api/endpoints/full | GET |
| /api/endpoints/<endpoint_id\> | GET |
| /api/endpoints/create_endpoint/dm | POST |
| /api/endpoints/create_endpoint/group/<title\> | POST |
| /api/endpoints/<group_id\>/create_invite | POST |
| /api/endpoints/<group_id\>/invites | GET |
| /api/endpoints/<group_id\>/invites | DELETE |
| /api/endpoints/join | GET POST |
| /api/endpoints/<group_id\>/leave | DELETE |
| /api/endpoints/<group_id\>/<user_id\>/kick | DELETE |

## [Message_routes](/docs/Message_routes.md)

| route | method |
| ----- | ------ |
| /api/endpoints/<endpoint_id\>/messages | GET |
| /api/endpoints/<endpoint_id\>/messages/<message_id\> | GET |
| /api/endpoints/<endpoint_id\>/messages/<message_id\>/from | GET |
| /api/endpoints/<endpoint_id\>/messages/<message_id\>/after | GET |
| /api/endpoints/<endpoint_id\>/messages/pinned | GET |
| /api/endpoints/<endpoint_id\>/messages/pinned/<message_id\>/pinned/from | GET |
| /api/endpoints/<endpoint_id\>/messages | POST |
| /api/endpoints/<endpoint_id\>/messages/<message_id\> | GET |
| /api/endpoints/<endpoint_id\>/messages/<message_id\> | DELETE |
| /api/endpoints/<endpoint_id\>/messages/<message_id\> | PATCH |
| /api/endpoints/<endpoint_id\>/messages/<message_id\>/pin | PATCH |
| /api/endpoints/<endpoint_id\>/messages/<message_id\>/unpin | PATCH |

## [File_routes](/docs/File_routes.md)

| route | method |
| ----- | ------ |
| /api/user/set_image | POST |
| /api/user/<user_id\>/profile_pic | GET |
| /api/files/upload | POST |
| /api/files/<file_name\> | GET |
