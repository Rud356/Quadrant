import fastjsonschema

user_self = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "_id": {"type": "string"},
        "created_at": {"type": "string"},
        "nick": {"type": "string"},
        "bot": {"type": "boolean"},
        "status": {"type": "integer"},
        "parent": {"type": "string"},
        "text_status": {"type": "string"},
        "blocked": {"type": "array"},
        "friends": {"type": "array"},
        "pendings_outgoing": {"type": "array"},
        "pendings_incoming": {"type": "array"},
    }
})

user_from_id = fastjsonschema.compile({
    "type": "object",
    "properties": {
        "_id": {"type": "string"},
        "created_at": {"type": "string"},
        "nick": {"type": "string"},
        "bot": {"type": "boolean"},
        "status": {"type": "integer"},
        "text_status": {"type": "string"},
    }
})