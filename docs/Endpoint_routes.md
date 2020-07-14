# Endpoint routes

## Route: /api/endpoints

Methods: GET

Requires: being authorized

Error codes:

- 401: unauthorized

Description:
Returns a list of channels ids where user is member

Response:

```json
["strings"]
```

## Route: /api/endpoints/full

Methods: GET

Requires: being authorized

Error codes:

- 401: unauthorized

Description:
Returns list of full channels (Channel objects might be `dm` or `group dm` only) objects

DM example:

```json
{
    "_id": "string",
    "_type": 0,
    "members": ["strings"],
    "created_at": "datetime",
    "last_message": "string",
    "last_pinned": "string"
}
```

Group DM example:

```json
{
    "_id": "string",
    "_type": 1,
    "members": ["strings"],
    "created_at": "datetime",
    "last_message": "string",
    "last_pinned": "string",

    "title": "string",
    "owner": "string",
    "owner_edits_only": "boolean"
}
```

[See more about _type value](/models/enums.py#L4-L9)

Response:

```json
{
    "_id": "channel",
    "_id 2": "channel"
}
```

Notice that these ids might be different and = to ids from previous route

## Route: /api/endpoints/<endpoint_id\>

Methods: GET

Requires: being authorized, endpoint id

Error codes:

- 401: unauthorized

- 404: invalid id or no such endpoint

Description: getting single channel with specified id where user is member

Response:
Single DM or Group DM object

## Route: /api/endpoints/create_endpoint/dm

Methods: POST

Requires: being authorized

```json
{
    "with": "user_id string"
}
```

Error codes:

- 401: unauthorized

- 404: Invalid user with id

- 409: already have dm, been blocked by each other, ivalid user

Description: starts dm with new user

Response:

```json
{
    "endpoint": {
        "_id": "string",
        "_type": 0,
        "members": ["strings"],
        "created_at": "datetime",
        "last_message": null,
        "last_pinned": null
    }
}
```

## Route: /api/endpoints/create_endpoint/group/<title\>

Methods: POST

Checks:

- Title length: from 1 symbol to 50 symbols (including both ends)

Error codes:

- 401: unauthorized

- 409: invalid title length

Description:
Creating group dm

Response:

```json
{
    "endpoint": {
        "_id": "string",
        "_type": 1,
        "members": ["strings"],
        "created_at": "datetime",
        "last_message": "string",
        "last_pinned": "string",
        "title": "string",
        "owner": "string",
        "owner_edits_only": "boolean"
    }
}
```

Errors:

- 400: too many invites existing

- 403: invites cant be created for that channel

- 404: invalid group id

## Route: /api/endpoints/<group_id\>/create_invite

Methods: POST

Requires: being authorized, being member of group, valid group id

Optional:

`expires_at` url param as int representing when will invite become invalid (in unix time, default 60 minutes)

`user_limit` url param as in representing how many times invite can be used (all values <= 0 will be counted as infinite, default = infinite)

Error codes:

- 400: too many invites existing (limit: 25)

- 401: unauthorized

- 403: invalid channel type

- 404: invalid group id

Description:
This method will return you a string containing invite code. `code` field represents the field you need to give other user in case you want him to join a group

Response:

```json
{
    "endpoint": "string",
    "user_created": "string",
    "user_limit": "integer",
    "code": "string",
    "users_passed": "integer",
    "expires_at": "float"
}
```

## Route: /api/endpoints/<group_id\>/invites

Methods: GET

Requires: being authorized, being a member

Error codes:

- 400: invalid channel `_type`

- 401: unauthorized

- 403: not a group member

- 404: invalid id

Description:
Returns all invites created for that group

// In future likely going to add more editions to let users hide those

Response:

```json
{
    {
        "endpoint": "string",
        "user_created": "string",
        "user_limit": "integer",
        "code": "string",
        "users_passed": "integer",
        "expires_at": "float"
    },
    {
        "endpoint": "string",
        "user_created": "string",
        "user_limit": "integer",
        "code": "string",
        "users_passed": "integer",
        "expires_at": "float"
    }, ...
}
```

## Route: /api/endpoints/<group_id\>/invites

Methods: DELETE

Requires: being authorized, being a member, having enough rights (for now - being owner of group), group id

`code` url param that representing our invite code

Error codes:

- 401: unauthorized

- 403: no permission

- 404: invalid group id or invalid channel type

Response: boolean that represents if invite was deleted (False if didn't existed)

## Route: /api/endpoints/join

Methods: GET POST

Requires: being authorized, `code` url param

Error codes:

- 400: no code provided or code is invalid

Response:

```json
{
    "endpoint": {
        "_id": "string",
        "_type": 1,
        "members": ["strings"],
        "created_at": "datetime",
        "last_message": "string",
        "last_pinned": "string",
        "title": "string",
        "owner": "string",
        "owner_edits_only": "boolean"
    }
}
```

## Route: /api/endpoints/<group_id\>/leave

Method: DELETE

Requires: being authorized, being group member

Error codes:

- 401: unauthorized

- 403: you are the creator of group (in future will add transferring ownership and deleting)

- 404: Invalid group id or channel type

Description:
Leaving group channel

Response: ok

## Route: /api/endpoints/<group_id\>/<user_id\>/leave

Method: DELETE

Requires: being authorized, being group member

Error codes:

- 400: not a member or invalid channel type

- 401: unauthorized

- 403: no permissions to kick

- 404: Invalid group id or channel type

Description:
Kicking user from group channel

Response: ok
