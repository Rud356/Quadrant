import fastjsonschema

from models.enums import Status


login = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "login": {
            "type": "string",
            "minLength": 6,
            "maxLength": 200
        },
        "password": {
            "type": "string",
            "minLength": 8,
            "maxLength": 256
        },
    },
    "required": ["password", "login"]
})


registrate_bot = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 25
        },
    },
    "required": ["nick"]
})


registrate = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 25
        },
        "login": {"type": "string", "default": ''},
        'password': {"type": "string", "default": ''},
    },
    "required": ["nick", "login", "password"]
})


message = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "content": {"type": "string", "maxLength": 3000},
        "files": {
            "type": "array",
            "items": {
                "type": "string",
                "maxLength": 15
            }
        }
    },
})


dm_endpoint = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "with": {"type": "string"}
    },
    "required": ["with"]
})


text_status = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "text_status": {"type": "string", "default": ''}
    },
    "required": ["text_status"]
})


status_codes = tuple(Status)
user_update = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {
            "type": "string",
            "minLength": 1,
            "maxLength": 25
        },
        "status": {"type": "integer"},
        "text_status": {
            "type": "string",
            "maxLength": 256
        },
        "friend_code": {
            "type": "string",
            "minLength": 3,
            "maxLength": 50
        },
    }}
)
