# File routes

## Route: /api/user/set_image

Methods: POST

Requires: image file uploaded as "image"

Checks:

- 4MB file size

- Formats: gif, jpeg, png, webp

Error codes:

- 400: Too big file, not selected any, incorrect format

- 401: unauthorized

Response: Profile image updated!

## Route: /api/user/<user_id\>/profile_pic

Methods: GET

Requires: Being authorized

Error codes:

- 404: invalid user id or no profile picture

Response: image file with x-filename header

## Route: /api/files/upload

Methods: POST

Requires: Being authorized

Checks:

- Default max size 20MB

Description:
Returning ids of uploaded files

Error codes:

- 401: unauthorized

Response:

```
["string", "string", ...]
```

### Route: /api/files/<file_name\>

Methods: GET

Requires: Being authorized, file name

Error codes:

- 401: unauthorized

- 404: invalid file

Response: file
