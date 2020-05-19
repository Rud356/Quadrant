import fastjsonschema

login = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "login": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["password", "login"]
})


registrate = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "nick": {"type": "string"},
        "bot": {"type": "boolean"},
        "login": {"type": "string", "default": ''},
        'password': {"type": "string", "default": ''},
        'parent': {"type": "string", "default": ''},
    },
    "required": ["nick", "bot"]
})


message = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "user_mentions": {"type": "array"},
        "files": {"type": "array"}
    },
    "required": ["content"]
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