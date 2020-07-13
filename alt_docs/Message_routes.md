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

Checks:

- Files existance

- At least existance of `content` or `files` key

- Content length <= 3000 symbols

Error codes:

- 400: too long message content, no content
- 401: unauthorized
- 403: not a group member

Response: ok
