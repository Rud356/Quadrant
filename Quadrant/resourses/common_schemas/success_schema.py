from marshmallow import Schema, fields


class SuccessResponseSchema(Schema):
    success = fields.Bool(default=True)
