from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.UUID()
    color_id = fields.Integer()
    username = fields.String()
    status = fields.String()
    text_status = fields.String(validate=[fields.validate.Length(min=0, max=256)])
    registered_at = fields.DateTime()
    is_bot = fields.Boolean()
    is_banned = fields.Boolean()


class UserPrivateSchema(UserSchema):
    common_settings = fields.Dict()
