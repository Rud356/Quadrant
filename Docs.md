# Routes
| ----- | ------ |
| route | method |
| ----- | ------ |
| /api/user/login | POST |
| /api/user/logout | GET POST DELETE |
| /api/user/register | POST |
| /api/user/<<user_id>> | GET |
| /api/user/me | GET |
| /api/me/nick?new_nick=<<new_nick>> | POST |
| /api/me/friend_code?=code<<new_code>> | POST |
| /api/me/status/<<new_status>>| POST |
| /api/me/test_status | POST |
| /api/friends | GET |
| /api/outgoing_requests | GET |
| /api/incoming_requests | GET |
| /api/friends/<<user_id>> | POST |
| /api/friends/<<user_id>> | DELETE |
| /api/friends/request?code=<<friendcode>> | POST |
| /api/incoming_requests/<<user_id>>?accept=<<bool>> | POST |
| /api/outgoing_requests/<<user_id>> | DELETE |
| /api/blocked | GET |
| /api/blocked/<<user_id>> | POST |
| /api/blocked/<<user_id>> | DELETE |
| ----- | ------ |
| /api/endpoints | GET |
| /api/endpoints/<<endpoint_id>> | GET |
| /api/endpoints/create_endpoint/dm | POST |
| ----- | ------ |
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
| ----- | ------ |
| /api/ws | WebSocket |
| ----- | ------ |
| /api/user/set_image | POST |
| /api/user/<<user_id>>/profile_pic | GET |
| /api/files/upload | POST |
| /api/files/<<file_id>> | GET |