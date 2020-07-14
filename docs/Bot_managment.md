# Bot managment

## Route: /api/bots

Methods: GET

Requires: Being authorized

Error codes:

- 401: unauthorized

Description:
Returns list of dictionaries with public users, that are bots

Response:

```json
{
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string"
}
```

## Route: /api/bots/registrate

Methods: POST

Requires: Being authorized

```json
{
    "nick": "string"
}
```

Checks:

- Nick length: 1 to 25 symbols

- Being not a bot

Description:
Creating a bot user for you

Response:

```json
{
    "_id": "string",
    "nick": "string",
    "created_at": "datetime",
    "bot": "boolean",
    "status": "integer",
    "text_status": "string",
    "friend_code": "string",
    "parent": "string",
    "blocked": [],
    "friends": [],
    "pendings_outgoing": [],
    "pendings_incoming": []
}
```

## Route: /api/bots/<bot_id\>/<nick\>

Methods: POST

Requires: Being authorized, bot id, nick (right into link)

Description:
Changes bots nick if valid

Checks:

- Nick length: 1 to 25 symbols

Error codes:

- 400: Invalid user (not a bots parent) or nick length

- 401: unauthorized

Response: ok

## Route: /api/bots/<bot_id\>/update_token

Methods: POST

Requires: Being authorized, bot id

Description:
Changes bots token

Error codes:

- 400: Invalid user (not a bots parent)

- 401: unauthorized

Response:

```json
{"new_token": "string"}
```

## Route: /api/bots/<bot_id\>

Methods: DELETE

Requires: Being authorized, bot id

Description:
Deletes bot (making unauthorizable)

Error codes:

- 400: Invalid user (not a bots parent)

Response: ok
