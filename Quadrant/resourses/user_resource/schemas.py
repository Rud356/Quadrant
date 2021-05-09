from marshmallow import Schema, fields


class UserRegistrationSchema(Schema):
    username = fields.String(required=True, validate=[fields.validate.Length(min=1, max=50)])
    # regex taken from: https://stackoverflow.com/questions/19605150/
    login = fields.String(
        required=True, validate=[
            fields.validate.Length(min=8, max=128),
            fields.validate.Regexp(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        ]
    )
    password = fields.String(
        required=True, validate=[
            fields.validate.Length(min=8, max=128),
            fields.validate.Regexp(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")
        ]
    )


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


class UserLoginResponseSchema(UserPrivateSchema):
    authorized = fields.Boolean(default=True)
    current_session_id = fields.Integer()
