# Relations routes

## Route: /api/friends/\<int:page>

Methods: GET

Requires: being authorized

Error codes:

- 401: unauthorized

Description:
Returning a page out of 100 friends users public dictionaries

Response:

```json
[
    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    },

    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    }, ...
]
```

## Route: /api/blocked/\<int:page>

Methods: GET

Requires: being authorized

Error codes:

- 401: unauthorized

Description:
Returning a page out of 100 blocked users public dictionaries

Response:

```json
[
    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    },

    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    }, ...
]
```

## Route: /api/incoming_requests/\<int:page>

Methods: GET

Requires: being authorized

Error codes:

- 401: unauthorized

Description:
Returning a page out of 100 incoming friend requests from users (public dictionaries)

Response:

```json
[
    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    },

    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    }, ...
]
```

## Route: /api/outgoing_requests/\<int:page>

Methods: GET

Requires: being authorized

Error codes:

- 401: unauthorized

Description:
Returning a page out of 100 outgoing friend requests from users (public dictionaries)

Response:

```json
[
    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    },

    {
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
    }, ...
]
```

## Route: /api/friends/\<id>

Methods: POST

Requires: Being authorized, id

Description:
Adds user to friends by _id

Error codes:

- 401: unauthorized

- 403: you are bot user

- 404: already sent request, cant do that, user doesn't exists

Description:
Sends friend request by user id

Response: ok

## Route: /api/friends/request

Methods: POST

Requires: being authorized, code (url param)

Checks:

- Code length: 1 to 50 symbols

Error codes:

- 400: no friend code

- 401: unauthorized

- 403: blocked, already in relations, you are bot

Description:
Sends friend request by code

Response: ok

## Route: /api/outgoing_requests/\<id>

Methods: DELETE

Requires: being authorized, user id

Error codes:

- 400: not sent friend request

- 401: unauthorized

- 403: you are bot

- 404: invalid id (not in outgiong)

Description:
Canceling friend request sent to someone

Response: ok

## Route: /api/incoming_requests/<id\>

Methods: POST

Requires: being authorized, user id

Optionally: accept (url param) can be set to `True` (exactly like that) (default cancelling request)

Error codes:

- 400: not sent friend request

- 401: unauthorized

- 403: you are bot

- 404: invalid id (not in incoming)

Description:
Responding to someone's request (by default cancelling, set accept param to `True` for accepting)

Response: ok

## Route: /api/friends/<id\>

Methods: DELETE

Requires: being authorized, friend id

Error codes:

- 400: user ain't a friend

- 401: unauthorized

- 403: you are bot

- 404: no such user

Description: delete user from friends

Response: ok

## Route: /api/blocked/<id\>

Methods: POST

Requires: being authorized, user id

Error codes:

- 204: already blocked

- 401: unauthorized

- 404: invalid user id

Description: blocking any user (bots also can do that)

Response: ok

## Route: /api/blocked/<id\>

Methods: DELETE

Requires: being authorized, user id

Error codes:

- 204: already unblocked

- 401: unauthorized

- 404: invalid user id

Description: unblocking blocked user (bots also can do that)

Response: ok
