# User routes

## Route: /api/user/login

Methods: POST

Requires:

```json
{
    "login": "string",
    "password": "string"
}
```

Error codes:

- 400: invalid json

- 401: invalid credentials

Description:
Authorizes regular user and returning private user json. Also setting a two days cookie with users token.

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
    "blocked": ["string"],
    "friends": ["string"],
    "pendings_outgoing": ["string"],
    "pendings_incoming": ["string"]
}
```

## Route: /api/user/register

Methods: POST

Requires:

```json
{
    "login": "string",
    "password": "string",
    "nick": "string"
}
```

Checks:

- Nick length: 1 to 25 symbols

- Login length: 5 to 200 symbols

- Password length: 8 to 255 symbols

Description:
Creating new user and automatically logs in

Error codes:

- 400: invalid one of fields

- 403: login already used

Response:
Same as login

## Route: /api/user/logout

Methods: POST GET DELETE

Requires: Being authorized

Checks: None

Description: cleans up user and goes offline

Error codes:

- 401: unauthorized

Response:
OK

## Route: /api/user/<id\>

Methods: GET

Requires: Being authorized

Description:
Returns user json

Description:
Returns information about user

Error codes:

- 400: invalid user id

- 401: unauthorized

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

## Route: /api/user/keep-alive

Methods: GET POST

Description:
Keeps user alive if has no websockets

Response: ok

## Route: /api/user/me

Methods: GET

Requires: Being authorized

Description:
Returns private user object

Error codes:

- 401: unauthorized

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
    "blocked": ["string"],
    "friends": ["string"],
    "pendings_outgoing": ["string"],
    "pendings_incoming": ["string"]
}
```

## Route: /api/user/me

Methods: DELETE

Requires: Being authorized

Description:
Makes user unauthorizable

Error codes:

- 401: unauthorized

Response: ok

## Route: /api/user/update_token

Methods: POST

Requires: Being authorized

Description:
Logs user out and making new token

Error codes:

- 401: unauthorized

Response: ok

## Route: /api/me/update

Methods: POST

Requires:

```json
{
    "nick": "string",
    "status": "integer",
    "text_status": "string",
    "friend_code": "string"
}
```

Checks:

- Nick length: 1 to 25 symbols

- Status: [Status codes](/models/enums.py)

- Text status length <= 256

- Friend code: should not be a bot user and length from 3 to 50

- Also MUST have at least one of those fields

Description:
Updates fields of user

Error codes:

- 400: No values provided or setting friend code as bot user (you can try to change friend code as bot user, but it won't give anything)

- 401: unauthorized

Response:
Same json as request
