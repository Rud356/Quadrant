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
        "login": {"type": "string", "default": ''},
        'password': {"type": "string", "default": ''},
    },
    "required": ["nick", "login", "password"]
})


message = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "content": {"type": "string"},
        "files": {"type": "array"}
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
