from marshmallow import Schema, fields


class JsonErrorSchema(Schema):
    status_code = fields.Integer()
    reason = fields.String()
