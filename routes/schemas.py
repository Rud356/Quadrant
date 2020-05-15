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