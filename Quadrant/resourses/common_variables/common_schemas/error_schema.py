from marshmallow import Schema, fields


class APIErrorSchema(Schema):
    status_code = fields.Int()
    reason = fields.Str()


class APIErrorWithNestedDataSchema(APIErrorSchema):
    reason = fields.Dict(keys=fields.Str(), values=fields.Str())
