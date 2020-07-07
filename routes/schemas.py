import fastjsonschema

from models.enums import Status


login = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "login": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["password", "login"]
})


registrate_bot = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {"type": "string"},
    },
    "required": ["nick"]
})


registrate = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {"type": "string"},
        "login": {"type": "string", "default": ''},
        'password': {"type": "string", "default": ''},
    },
    "required": ["nick", "login", "password"]
})


message = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "files": {
            "type": "array",
            "items": {
                "type": "string"
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


user_update = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {"type": "string"},
        "status": {"type": "number"},
        "text_status": {"type": "string"},
        "friend_code": {"type": "string"}
    }},
    formats={
        "nick": lambda val: len(val.strip(' \n\t')) in range(1, 25 + 1),
        "status": lambda val: val in list(Status),
        "text_status": lambda val: len(val.strip(' \n\t')) <= 256,
        "friend_code": lambda val: len(val.strip(' \n\t')) in range(3, 51)
})
