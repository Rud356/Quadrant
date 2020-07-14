# Message routes

## Route: /api/endpoints/<endpoint_id\>/messages

Methods: POST

Requires: endpoint id, being authorized, being endpoint member

```json
{
    "content": "string",
    "files": ["strings with file id"]
}
```

Description:
Sending some message

Checks:

- Files existance

- At least existance of `content` or `files` key

- Content length <= 3000 symbols

Error codes:

- 400: too long message content, no content
- 401: unauthorized
- 403: not a group member
- 404: no such endpoint, invalid id

Response: ok

## Route: /api/endpoints/<endpoint_id\>/messages

Methods: GET

Requires: endpoint id, being authorized, being endpoint member

Description:
Returns list of latest messages

Checks:

- Files existance

- At least existance of `content` or `files` key

- Content length <= 3000 symbols

Error codes:

- 401: unauthorized
- 403: not a group member
- 404: no such endpoint

Description:
Returns list of 100 latests messages sorted from new to old

Response:

```json
[
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    },
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    }, ...
]
```

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>

Methods: GET

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 401: unauthorized
- 403: not a group member
- 404: no such message or endpoint

Description:
Returning only one message from one channel with given id

Response:

```json
{
    "_id": "string",
    "author": "string",
    "endpoint": "string",
    "content": "string",
    "files": ["strings"],
    "created_at": "datetime",
    "pin": "boolean",
    "edited": "boolean"
}
```

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>/from

Methods: GET

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 401: unauthorized
- 403: not a group member
- 404: no such endpoint

Description:
Returning 100 messages sorted from newest to oldest that has been sent before specific one (not including the one in request)

Response:

```json
[
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    },
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    }, ...
]
```

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>/after

Methods: GET

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 401: unauthorized
- 403: not a group member
- 404: no such endpoint

Description:
Returning 100 messages sorted from newest to oldest that has been sent after (later than) specific one (not including the one in request)

Response:

```json
[
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    },
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    }, ...
]
```

## Route: /api/endpoints/<endpoint_id\>/messages/pinned

Methods: GET

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 401: unauthorized
- 403: not a group member
- 404: no such endpoint

Description:
Returning 100 latest messages sorted from newest to oldest that has been pinned

Response:

```json
[
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    },
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    }, ...
]
```

## Route: /api/endpoints/<endpoint_id\>/messages/pinned/<message_id\>/pinned/from

Methods: GET

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 401: unauthorized
- 403: not a group member
- 404: no such endpoint

Description:
Returning 100 messages sorted from newest to oldest that has been sent before specified one (excluding specified one)

Response:

```json
[
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    },
    {
        "_id": "string",
        "author": "string",
        "endpoint": "string",
        "content": "string",
        "files": ["strings"],
        "created_at": "datetime",
        "pin": "boolean",
        "edited": "boolean"
    }, ...
]
```

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>

Methods: DELETE

Requires: endpoint id, message id, being authorized, being endpoint member

Optionally: you can specify `force` param in url to value `True`, if you want to force delete message (deletes anyone's message, if you have rights)

Error codes:

- 204: Nothing to delete

- 400: Invalid id or invalid endpoint id

- 401: unauthorized

- 403: not a group member, cant force delete message or endpoint not allowing to force delete messages

Response: ok

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>

Methods: PATCH

Requires: endpoint id, message id, being authorized, being endpoint member

```json
{
    "content": "string"
}
```

Checks: new content length should be in range from 1 symbol to 3000 (including both ends)

Error codes:

- 204: not modified

- 400: no content to modify

- 401: unauthorized

- 403: you aren't group member

- 404: no such endpoint, invalid id of endpoint or message

Description: modifying message content

Response: ok

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>/pin

Methods: PATCH

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 204: nothing pinned

- 401: unauthorized

- 403: not a group member or no permissions

- 404: invalid message id, or channel id

Description: pins message

Response: ok

## Route: /api/endpoints/<endpoint_id\>/messages/<message_id\>/unpin

Methods: PATCH

Requires: endpoint id, message id, being authorized, being endpoint member

Error codes:

- 204: nothing unpinned

- 401: unauthorized

- 403: not a group member or no permissions

- 404: invalid message id, or channel id

Description: pins message

Response: ok
